import sys
import time
import tkinter
import math
from envs import layouts
from envs.game_state import GameState
from .renderers import BaseDisplay

class TkinterDisplay(BaseDisplay):
    def __init__(self, zoom: float = 1.0, frame_time: float = 0.0, title="Pacman"):
        super().__init__(zoom=zoom, frame_time=frame_time)
        self.grid_size = layouts.GRID_SIZE * zoom 
        self.shapes = {}
        self.pacman_shape = None
        self.ghost_shapes = {} 

        self._root = None
        self._canvas = None
        self._window_closed = False
        self._title = title

        self.PACMAN_RADIUS = layouts.PACMAN_RADIUS
        self.FOOD_RADIUS = layouts.FOOD_RADIUS
        self.CAPSULE_RADIUS = layouts.CAPSULE_RADIUS
        self.GHOST_RADIUS = layouts.GHOST_RADIUS
        self.WALL_COLOR = layouts.WALL_COLOR
        self.WALL_OUTLINE = layouts.WALL_OUTLINE
        self.FOOD_COLOR = layouts.FOOD_COLOR
        self.CAPSULE_COLOR = layouts.CAPSULE_COLOR
        self.PACMAN_COLOR = layouts.PACMAN_COLOR
        self.GHOST_COLORS = layouts.GHOST_COLORS
        self.SCARED_COLOR = layouts.SCARED_COLOR

    def _formatColor(self, r, g, b):
        return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))

    def _sleep(self, secs):
        if self._root is None:
            time.sleep(secs)
        else:
            end = time.time() + secs
            while time.time() < end:
                try:
                    self._root.update()
                except:
                    self._window_closed = True
                    break
                time.sleep(0.01)

    def _begin_graphics(self, width, height, color=None):
        if color is None:
            color = self._formatColor(0, 0, 0)
        if self._root:
            self._root.destroy()
        self._root = tkinter.Tk()
        self._root.title(self._title)
        self._root.resizable(0, 0)
        self._root.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
        self._canvas = tkinter.Canvas(self._root, width=width, height=height, bg=color, highlightthickness=0)
        self._canvas.pack()
        self._window_closed = False

    def _circle(self, pos, r, outlineColor, fillColor, endpoints=None, width=2):
        x, y = pos
        x0, x1 = x - r, x + r
        y0, y1 = y - r, y + r
        e = [0, 359] if endpoints is None else list(endpoints)
        while e[0] > e[1]: e[1] += 360
        return self._canvas.create_arc(x0, y0, x1, y1, outline=outlineColor, fill=fillColor,
                                        extent=e[1] - e[0], start=e[0], style="pieslice", width=width)

    def _text(self, pos, color, contents, size=12, style="normal", anchor="nw"):
        return self._canvas.create_text(pos[0], pos[1], fill=color, text=contents,
                                        font=("Courier", str(size), style), anchor=anchor)

    def _changeText(self, id, newText):
        self._canvas.itemconfigure(id, text=newText)

    def _refresh(self):
        if self._canvas: self._canvas.update_idletasks()
        if self._root: self._root.update()

    def _remove_from_screen(self, id):
        if self._canvas and id: self._canvas.delete(id)

    def _end_graphics(self):
        if self._root:
            self._root.destroy()
            self._root = None
            self._canvas = None

    def initialize(self, state: GameState):
        h, w = state.object_matrix.shape
        self._begin_graphics(w * self.grid_size, (h + 1) * self.grid_size)
        self.score_id = self._text((10, h * self.grid_size + 5), "white", "Score: 0")

    def update(self, state: GameState):
        mat = state.object_matrix
        h, w = mat.shape
        
        current_frame_objects = set()

        for y in range(h):
            for x in range(w):
                val = mat[y, x]
                pos = (x, y)
                
                if val == layouts.WALL:
                    current_frame_objects.add(pos)
                    if pos not in self.shapes:
                        x0, y0 = x * self.grid_size, y * self.grid_size
                        x1, y1 = x0 + self.grid_size, y0 + self.grid_size
                        self.shapes[pos] = self._canvas.create_rectangle(
                            x0, y0, x1, y1, fill=self.WALL_COLOR, outline=self.WALL_OUTLINE
                        )

                elif val == layouts.FOOD:
                    current_frame_objects.add(pos)
                    if pos not in self.shapes:
                        r = self.grid_size * self.FOOD_RADIUS
                        cx, cy = (x + 0.5) * self.grid_size, (y + 0.5) * self.grid_size
                        self.shapes[pos] = self._canvas.create_rectangle(
                            cx - r, cy - r, cx + r, cy + r,
                            fill=self.FOOD_COLOR, outline=""
                        )

                elif val == layouts.CAPSULE:
                    current_frame_objects.add(pos)
                    color = self.CAPSULE_COLOR if int(time.time() * 4) % 2 == 0 else "white"
                    if pos in self.shapes:
                        self._canvas.itemconfig(self.shapes[pos], fill=color, outline=color)
                    else:
                        r = self.grid_size * self.CAPSULE_RADIUS
                        cx, cy = (x + 0.5) * self.grid_size, (y + 0.5) * self.grid_size
                        self.shapes[pos] = self._canvas.create_oval(
                            cx - r, cy - r, cx + r, cy + r, fill=color, outline=color
                        )

        old_positions = list(self.shapes.keys())
        for pos in old_positions:
            if pos not in current_frame_objects:
                self._remove_from_screen(self.shapes[pos])
                del self.shapes[pos]

        if state.pacman:
            self._render_pacman(state.pacman.x, state.pacman.y, state.pacman.dir)

        for i, ghost in enumerate(state.ghosts):
            self._render_ghost(i, ghost.x, ghost.y, state)

        self._changeText(self.score_id, f"Score: {int(state.score)}")
        self._refresh()

    def _clear_ghost(self, idx):
        if idx in self.ghost_shapes:
            for id in self.ghost_shapes[idx]:
                self._remove_from_screen(id)
            self.ghost_shapes[idx] = []

    def _render_pacman(self, x, y, direction):
        if self.pacman_shape:
            self._remove_from_screen(self.pacman_shape)

        cx = x * self.grid_size + self.grid_size / 2
        cy = y * self.grid_size + self.grid_size / 2
        r = self.grid_size * self.PACMAN_RADIUS

        angle_map = {
            "North": 90, "South": 270, "East": 0, "West": 180,
            "Up": 90, "Down": 270, "Left": 180, "Right": 0,
            "Stop": 0
        }
        
        base_angle = angle_map.get(direction, 0)
        mouth_width = 45 * abs(math.sin(time.time() * 18))
        
        self.pacman_shape = self._canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            fill=self.PACMAN_COLOR, outline=self.PACMAN_COLOR,
            start=base_angle + (mouth_width / 2),
            extent=360 - mouth_width, 
            style="pieslice"
        )

    def _render_ghost(self, idx, x, y, state):
        self._clear_ghost(idx)
        self.ghost_shapes[idx] = []

        cx, cy = (x + 0.5) * self.grid_size, (y + 0.5) * self.grid_size
        r = self.grid_size * self.GHOST_RADIUS
        
        ghost_obj = state.ghosts[idx]
        scared = ghost_obj.scared_timer > 0
        color = self.SCARED_COLOR if scared else self.GHOST_COLORS[idx % len(self.GHOST_COLORS)]

        self.ghost_shapes[idx].append(self._canvas.create_arc(cx-r, cy-r, cx+r, cy+r/2, start=0, extent=180, fill=color, outline=color))
        self.ghost_shapes[idx].append(self._canvas.create_rectangle(cx-r, cy, cx+r, cy+r*0.7, fill=color, outline=color))
        
        for i in range(3):
            x0 = (cx - r) + (i * (2*r/3))
            self.ghost_shapes[idx].append(self._canvas.create_oval(x0, cy+r*0.5, x0+(2*r/3), cy+r, fill=color, outline=color))

        for offset in [-0.4, 0.4]:
            ex, ey = cx + offset * r, cy - r*0.3
            self.ghost_shapes[idx].append(self._canvas.create_oval(ex-3, ey-4, ex+3, ey+4, fill="white", outline="white"))
            if not scared:
                self.ghost_shapes[idx].append(self._canvas.create_oval(ex-1, ey-1, ex+1, ey+1, fill="black"))

    def finish(self):
        self._end_graphics()

    def mainloop(self):
        if self._root: self._root.mainloop()

    def get_root(self):
        return self._root