import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ""))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from frontend.socket_client import SocketClient
from config.agent_config import AGENT_SETTINGS
from config.socket_config import HOST, PORT


class ControlPanel(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.client = None
        self._algo_procs = {}
        self._agent_algo_vars = {}
        self._agent_status_texts = {}
        self._agent_key_rects = {}
        self._agent_key_texts = {}
        self.agent_cols = []
        self.paused = False

        self.setup_layout()
        self.create_agent_columns()

        self.connect_backend()
        self.start_polling()

        self.after(100, self.bootstrap_agents)

    def setup_layout(self):
        self.left_frame = tk.Frame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.right_frame = tk.Frame(self)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ttk.Button(self.left_frame, text="Pause Game", command=self.pause_game)\
            .grid(row=0, column=0, pady=5, sticky="ew")

        ttk.Button(self.left_frame, text="Unpause Game", command=self.unpause_game)\
            .grid(row=1, column=0, pady=5, sticky="ew")

        ttk.Button(self.left_frame, text="Stop All Algorithms", command=self.stop_all_workers)\
            .grid(row=10, column=0, pady=20, sticky="ew")

        self.columns_container = tk.Frame(self.right_frame)
        self.columns_container.pack(fill="both", expand=True)

    def pause_game(self):
        self.paused = True
        if self.client and self.client.sock:
            self.client.send({"type": "command", "cmd": "pause"})

    def unpause_game(self):
        self.paused = False
        if self.client and self.client.sock:
            self.client.send({"type": "command", "cmd": "unpause"})

    def create_agent_columns(self):
        for i in range(3):
            col = tk.Frame(
                self.columns_container,
                width=220,
                bg="#fff",
                highlightthickness=1,
                highlightbackground="#eee"
            )
            col.pack(side="left", fill="both", expand=True, padx=8)
            self.agent_cols.append(col)
            self._setup_single_agent_ui(i, col)

    def _setup_single_agent_ui(self, idx, parent_col):
        config = AGENT_SETTINGS.get(idx)

        tk.Label(
            parent_col,
            text=config["name"],
            font=("Arial", 12, "bold"),
            bg="#fff"
        ).pack(anchor="nw", padx=10, pady=(10, 5))

        canvas = tk.Canvas(
            parent_col,
            width=180,
            height=140,
            bg="#fff",
            highlightthickness=1,
            highlightbackground="#ddd"
        )
        canvas.pack(padx=10, pady=5)
        self._draw_direction_arrows(idx, canvas)

        var = tk.StringVar(value=config["default"])
        combo = ttk.Combobox(
            parent_col,
            textvariable=var,
            values=config["available_algos"],
            state="readonly",
            width=15
        )
        combo.pack(anchor="w", padx=10, pady=5)
        combo.bind(
            "<<ComboboxSelected>>",
            lambda e, agent_idx=idx, v=var: self.on_algo_changed(agent_idx, v.get())
        )

        self._agent_algo_vars[idx] = var

        st = tk.Label(
            parent_col,
            text="Last: -",
            fg="#666",
            bg="#fff",
            font=("Arial", 10)
        )
        st.pack(anchor="w", padx=10)
        self._agent_status_texts[idx] = st

    def _draw_direction_arrows(self, idx, canvas):
        cx, cy = 90, 70
        arrows = {"Up": "↑", "Left": "←", "Down": "↓", "Right": "→"}
        pos_map = {
            "Up": (cx - 15, cy - 45, cx + 15, cy - 15),
            "Left": (cx - 45, cy - 15, cx - 15, cy + 15),
            "Down": (cx - 15, cy - 15, cx + 15, cy + 15),
            "Right": (cx + 15, cy - 15, cx + 45, cy + 15),
        }

        rects, texts = {}, {}
        for k, pos in pos_map.items():
            rects[k] = canvas.create_rectangle(
                *pos, fill="#ffffff", outline="#bbb", width=1
            )
            texts[k] = canvas.create_text(
                (pos[0] + pos[2]) / 2,
                (pos[1] + pos[3]) / 2,
                text=arrows[k],
                font=("Arial", 12)
            )

        self._agent_key_rects[idx] = rects
        self._agent_key_texts[idx] = texts

    def start_worker_process(self, agent_idx, algo):
        self.stop_single_worker(agent_idx)
        time.sleep(0.1)

        worker_path = os.path.join(PROJECT_ROOT, "workers", "agent_worker.py")
        if not os.path.exists(worker_path):
            return

        env = os.environ.copy()
        env["PYTHONPATH"] = PROJECT_ROOT + os.pathsep + env.get("PYTHONPATH", "")

        cmd = [sys.executable, worker_path, str(agent_idx), algo]
        process = subprocess.Popen(
            cmd,
            env=env,
            cwd=PROJECT_ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        self._algo_procs[agent_idx] = process

    def stop_single_worker(self, agent_idx):
        proc = self._algo_procs.pop(agent_idx, None)
        if proc and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=1)
            except:
                try:
                    proc.kill()
                except:
                    pass

    def stop_all_workers(self):
        for idx in list(self._algo_procs.keys()):
            self.stop_single_worker(idx)

    def connect_backend(self):
        if not self.client:
            self.client = SocketClient(HOST, PORT)

        if not self.client.sock:
            if self.client.connect():
                self.sync_all_algos_to_backend()
            else:
                self.after(1000, self.connect_backend)

    def sync_all_algos_to_backend(self):
        for i in range(3):
            algo = self._agent_algo_vars[i].get()
            self.client.send({
                "type": "command",
                "cmd": "set_algo",
                "agent": i,
                "algo": algo
            })

    def on_algo_changed(self, agent_idx, algo_name):
        if self.client and self.client.sock:
            self.client.send({
                "type": "command",
                "cmd": "set_algo",
                "agent": agent_idx,
                "algo": algo_name
            })
        self.start_worker_process(agent_idx, algo_name)

    def bootstrap_agents(self):
        for i in range(3):
            self.start_worker_process(i, self._agent_algo_vars[i].get())

    def start_polling(self):
        self.poll_agent_actions()

    def poll_agent_actions(self):
        if self.client and self.client.sock:
            try:
                self.client.send({"type": "get_status"})
                status = self.client.recv(timeout=0.05) or {}
                self.update_ui_from_status(status)
            except:
                pass
        self.after(150, self.poll_agent_actions)

    def update_ui_from_status(self, status):
        last_exec = status.get("last_executed", {})
        for i in range(3):
            act = last_exec.get(str(i)) or last_exec.get(i)
            if act and act != "-":
                self._agent_status_texts[i].config(text=f"Last: {act}")
                self.highlight_arrow(i, act)

    def highlight_arrow(self, agent_idx, action):
        if agent_idx not in self._agent_key_rects:
            return

        canvas = self.agent_cols[agent_idx].winfo_children()[1]

        for rect_id in self._agent_key_rects[agent_idx].values():
            canvas.itemconfig(rect_id, fill="#ffffff", outline="#bbb", width=1)

        action_map = {
            "North": "Up",
            "South": "Down",
            "West": "Left",
            "East": "Right",
            "Up": "Up",
            "Down": "Down",
            "Left": "Left",
            "Right": "Right"
        }

        key = action_map.get(str(action), None)
        if key and key in self._agent_key_rects[agent_idx]:
            canvas.itemconfig(
                self._agent_key_rects[agent_idx][key],
                fill="#bbdefb",
                outline="#1e88e5",
                width=2
            )


    def on_app_closing(self):
        self.stop_all_workers()
        if self.client:
            self.client.close()
        self.master.destroy()
        os._exit(0)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Pacman Control Panel")
    root.geometry("810x270")
    panel = ControlPanel(root)
    panel.pack(fill="both", expand=True)
    root.protocol("WM_DELETE_WINDOW", panel.on_app_closing)
    root.mainloop()
