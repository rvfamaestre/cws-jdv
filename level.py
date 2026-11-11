import json
import os
from universe import Universe
from cell import ALIVE, PERMANENT, OBJECTIVE
from constants import GRID_ROWS, GRID_COLS

LEVELS_DIR = os.path.join(os.path.dirname(__file__), "levels")


class Level:
    def __init__(self, name, rows=GRID_ROWS, cols=GRID_COLS):
        self.name = name
        self.rows = rows
        self.cols = cols
        self.permanents = []  # list of (r, c)
        self.alive_cells = []  # list of (r, c)
        self.objectives = []  # list of (r, c)
        self.start_zone = None  # (r1, c1, r2, c2) or None
        self.music_track = None  # optional filename in assets/sfx (e.g. soundtrack1.wav)

    def build_universe(self):
        uni = Universe(self.rows, self.cols)
        for r, c in self.permanents:
            uni.set_cell(r, c, PERMANENT)
        for r, c in self.alive_cells:
            uni.set_cell(r, c, ALIVE)
        for r, c in self.objectives:
            uni.set_cell(r, c, OBJECTIVE)
        return uni

    def save(self):
        os.makedirs(LEVELS_DIR, exist_ok=True)
        data = {
            "name": self.name,
            "rows": self.rows,
            "cols": self.cols,
            "permanents": self.permanents,
            "alive_cells": self.alive_cells,
            "objectives": self.objectives,
            "start_zone": self.start_zone,
            "music_track": self.music_track,
        }
        path = os.path.join(LEVELS_DIR, f"{self.name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load(name):
        path = os.path.join(LEVELS_DIR, f"{name}.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        lvl = Level(
            data["name"], data.get("rows", GRID_ROWS), data.get("cols", GRID_COLS)
        )
        lvl.permanents = [tuple(p) for p in data.get("permanents", [])]
        lvl.alive_cells = [tuple(p) for p in data.get("alive_cells", [])]
        lvl.objectives = [tuple(p) for p in data.get("objectives", [])]
        lvl.start_zone = tuple(data["start_zone"]) if data.get("start_zone") else None
        lvl.music_track = data.get("music_track")
        return lvl

    @staticmethod
    def list_levels():
        os.makedirs(LEVELS_DIR, exist_ok=True)
        return [f[:-5] for f in os.listdir(LEVELS_DIR) if f.endswith(".json")]
