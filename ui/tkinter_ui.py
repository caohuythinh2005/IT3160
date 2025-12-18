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
        self.grid_size = layouts.GRID_SIZE
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

    def _polygon(self, coords, outlineColor, fillColor=None, filled=1, width=1):
        c = []
        for coord in coords:
            c.extend([coord[0], coord[1]])
        if fillColor is None: fillColor = outlineColor
        if not filled: fillColor = ""
        return self._canvas.create_polygon(c, outline=outlineColor, fill=fillColor, width=width)

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
        for y, row in enumerate(mat):
            for x, val in enumerate(row):
                pos = (x, y)

                if val == layouts.WALL:
                    if pos not in self.shapes:
                        x0, y0 = x * self.grid_size, y * self.grid_size
                        x1, y1 = x0 + self.grid_size, y0 + self.grid_size
                        self.shapes[pos] = self._canvas.create_rectangle(
                            x0, y0, x1, y1, fill=self.WALL_COLOR, outline=self.WALL_OUTLINE
                        )

                elif val in (layouts.FOOD, layouts.CAPSULE):
                    if pos not in self.shapes:
                        radius = self.CAPSULE_RADIUS if val == layouts.CAPSULE else self.FOOD_RADIUS
                        color = self.CAPSULE_COLOR if val == layouts.CAPSULE else self.FOOD_COLOR
                        sp = ((x + 0.5) * self.grid_size, (y + 0.5) * self.grid_size)
                        self.shapes[pos] = self._circle(sp, self.grid_size * radius, color, color)

                else:
                    if pos in self.shapes and val not in (layouts.WALL, layouts.PACMAN,
                                                         layouts.GHOST1, layouts.GHOST2,
                                                         layouts.GHOST3, layouts.GHOST4):
                        self._remove_from_screen(self.shapes[pos])
                        del self.shapes[pos]

                if val == layouts.PACMAN:
                    self._render_pacman(x, y, state.pacman.dir)

                if val in (layouts.GHOST1, layouts.GHOST2, layouts.GHOST3, layouts.GHOST4):
                    self._render_ghost(val, x, y, state)

        self._changeText(self.score_id, f"Score: {int(state.score)}")
        self._refresh()

    def _render_pacman(self, x, y, dir):
        if self.pacman_shape:
            self._remove_from_screen(self.pacman_shape)
        sp = (x * self.grid_size + self.grid_size / 2, y * self.grid_size + self.grid_size / 2)
        angles = {1: 90, 2: 0, 3: 270, 4: 180}.get(dir, 0)
        width = 30 + 80 * math.sin(math.pi * ((x % 1) + (y % 1)))
        self.pacman_shape = self._circle(sp, self.grid_size * self.PACMAN_RADIUS,
                                        self.PACMAN_COLOR, self.PACMAN_COLOR,
                                        endpoints=(angles + width / 2, angles - width / 2))

    def _render_ghost(self, val, x, y, state):
        idx = val - layouts.GHOST1
        if idx in self.ghost_shapes:
            self._remove_from_screen(self.ghost_shapes[idx])
        sp = (x * self.grid_size + self.grid_size / 2, y * self.grid_size + self.grid_size / 2)
        color = self.SCARED_COLOR if getattr(state, 'is_ghost_scared', lambda i: False)(idx) else \
            self.GHOST_COLORS[idx % len(self.GHOST_COLORS)]
        self.ghost_shapes[idx] = self._circle(sp, self.grid_size * self.GHOST_RADIUS, color, color)

    def finish(self):
        self._end_graphics()

    def after(self, delay_ms, callback):
        if self._root:
            self._root.after(delay_ms, callback)

    def mainloop(self):
        if self._root:
            self._root.mainloop()

    def get_root(self):
        return self._root
