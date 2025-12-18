import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk

# ---- Paths ----
current_file_path = os.path.abspath(__file__)
project_root = os.path.abspath(os.path.join(os.path.dirname(current_file_path)))
src_path = project_root
if src_path not in sys.path:
    sys.path.append(src_path)
if project_root not in sys.path:
    sys.path.append(project_root)

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

        self.create_widgets()
        self.bind_all("<Key>", self.on_key)
        self._init_agent_panels()
        self._bootstrap_agents()
        self._ensure_backend_connected()  # auto connect backend
        self._poll_agent_actions()

    # ---- UI Widgets ----
    def create_widgets(self):
        self.left_frame = tk.Frame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.right_frame = tk.Frame(self)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        buttons = [
            ("w", "W / Up"), ("a", "A / Left"), ("s", "S / Down"), ("d", "D / Right"),
            ("Up", "↑ Arrow Up"), ("Left", "← Arrow Left"), ("Down", "↓ Arrow Down"), ("Right", "→ Arrow Right")
        ]
        for i, (k, label) in enumerate(buttons):
            ttk.Button(self.left_frame, text=label, width=20, 
                       command=lambda key=k: self.send_key(key)).grid(row=i, column=0, pady=2, sticky="ew")

        ttk.Button(self.left_frame, text="Stop All Algorithms", command=self._stop_all_algo_processes).grid(row=10, column=0, pady=5, sticky="ew")

        columns_frame = tk.Frame(self.right_frame)
        columns_frame.pack(fill="both", expand=True)
        for i in range(3):
            col = tk.Frame(columns_frame, width=220, bg="#fff", highlightthickness=1, highlightbackground="#eee")
            col.pack(side="left", fill="both", expand=True, padx=8)
            self.agent_cols.append(col)

    # ---- Agent Panels ----
    def _init_agent_panels(self):
        arrows = {"Up":"↑","Left":"←","Down":"↓","Right":"→"}
        for idx in range(3):
            config = AGENT_SETTINGS.get(idx)
            col = self.agent_cols[idx]
            tk.Label(col, text=config["name"], font=("Arial", 12, "bold"), bg="#fff").pack(anchor="nw", padx=10, pady=(10,5))
            
            c = tk.Canvas(col, width=180, height=140, bg="#fff", highlightthickness=1, highlightbackground="#ddd")
            c.pack(padx=10, pady=5)
            
            cx, cy = 90, 70
            rects, texts = {}, {}
            pos_map = {
                "Up": (cx-15, cy-45, cx+15, cy-15),
                "Left": (cx-45, cy-15, cx-15, cy+15),
                "Down": (cx-15, cy-15, cx+15, cy+15),
                "Right": (cx+15, cy-15, cx+45, cy+15)
            }
            for k, pos in pos_map.items():
                rects[k] = c.create_rectangle(*pos, fill="#fff", outline="#bbb")
                texts[k] = c.create_text((pos[0]+pos[2])/2, (pos[1]+pos[3])/2, text=arrows[k], font=("Arial", 12))
            
            self._agent_key_rects[idx], self._agent_key_texts[idx] = rects, texts

            var = tk.StringVar(value=config["default"])
            combo = ttk.Combobox(col, textvariable=var, values=config["available_algos"], state="readonly", width=15)
            combo.pack(anchor="w", padx=10, pady=5)
            combo.bind("<<ComboboxSelected>>", lambda e, i=idx, v=var: self._on_algo_selected(i, v.get()))
            self._agent_algo_vars[idx] = var

            st = tk.Label(col, text="Last: -", fg="#666", bg="#fff", font=("Arial", 10))
            st.pack(anchor="w", padx=10)
            self._agent_status_texts[idx] = st

    # ---- Agent Startup ----
    def _bootstrap_agents(self):
        for i in range(3):
            default_algo = self._agent_algo_vars[i].get()
            self._on_algo_selected(i, default_algo)

    # ---- Always try connect backend ----
    def _ensure_backend_connected(self):
        if not self.client:
            self.client = SocketClient(HOST, PORT)
        if not self.client.sock:
            if self.client.connect():
                for i in range(3):
                    algo = self._agent_algo_vars[i].get()
                    self.client.send({"type": "command", "cmd": "set_algo", "agent": i, "algo": algo})
                print("[UI] Connected to Backend.")
            else:
                print("[UI] Backend not ready. Retrying in 1s...")
                self.after(1000, self._ensure_backend_connected)

    # ---- Highlight ----
    def _highlight_direction(self, agent_idx, action):
        if agent_idx not in self._agent_key_rects: return
        canvas = self.agent_cols[agent_idx].winfo_children()[1]
        for k in self._agent_key_rects[agent_idx]:
            canvas.itemconfig(self._agent_key_rects[agent_idx][k], fill="#fff")
        
        act_key = str(action).title()
        if act_key in self._agent_key_rects[agent_idx]:
            canvas.itemconfig(self._agent_key_rects[agent_idx][act_key], fill="#e1f5fe", outline="#03a9f4")

    # ---- Algorithm Selection ----
    def _on_algo_selected(self, agent_idx, algo):
        if self.client and self.client.sock:
            self.client.send({"type": "command", "cmd": "set_algo", "agent": agent_idx, "algo": algo})
        if algo.lower() != "keyboard":
            self._start_algo_process(agent_idx, algo)
        else:
            self._stop_algo_process(agent_idx)

    def _start_algo_process(self, agent_idx, algo):
        self._stop_algo_process(agent_idx)
        worker_path = os.path.join(project_root, "workers", "agent_worker.py")
        
        if not os.path.exists(worker_path):
            print(f"[UI] Error: Worker path not found: {worker_path}")
            return

        env = os.environ.copy()
        env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")
        
        print(f"[UI] Starting worker for Agent {agent_idx} ({algo})...")
        self._algo_procs[agent_idx] = subprocess.Popen(
            [sys.executable, worker_path, str(agent_idx), algo],
            env=env, 
            cwd=project_root,
            stdout=subprocess.DEVNULL
        )

    def _stop_algo_process(self, agent_idx):
        proc = self._algo_procs.pop(agent_idx, None)
        if proc and proc.poll() is None: 
            proc.terminate()
            print(f"[UI] Stopped worker for Agent {agent_idx}")

    def _stop_all_algo_processes(self):
        for idx in list(self._algo_procs.keys()): 
            self._stop_algo_process(idx)

    # ---- Keyboard Control ----
    def send_key(self, key, agent_idx=0):
        mapping = {"w":"Up","a":"Left","s":"Down","d":"Right"}
        action = mapping.get(key.lower(), key)
        if self.client and self.client.sock and self._agent_algo_vars[agent_idx].get().lower() == "keyboard":
            self.client.send({"type": "action", "agent": agent_idx, "action": action})

    def on_key(self, event):
        if event.keysym in ["w","a","s","d","Up","Down","Left","Right"]:
            self.send_key(event.keysym, 0)

    # ---- Polling Agent Actions ----
    def _poll_agent_actions(self):
        # retry backend if disconnected
        if not self.client or not self.client.sock:
            self._ensure_backend_connected()
        else:
            try:
                self.client.send({"type": "get_status"})
                status = self.client.recv(timeout=0.05) or {}
                last_exec = status.get("last_executed", {})
                for i in range(3):
                    act = last_exec.get(str(i)) or last_exec.get(i)
                    if act and act != "-": 
                        self._agent_status_texts[i].config(text=f"Last: {act}")
                        self._highlight_direction(i, act)
            except:
                pass
        self.after(150, self._poll_agent_actions)

# ---- Main ----
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Pacman Control Panel")
    root.geometry("830x330")
    panel = ControlPanel(root)
    panel.pack(fill="both", expand=True)
    
    def on_closing():
        panel._stop_all_algo_processes()
        if panel.client: panel.client.close()
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
