# Play and controls

Run commands from the repository root.

```bash
pip install pygame
python main.py
```

Select a level from the menu. In **setup mode**, click cells in the highlighted start zone to place or remove living cells. Press **Space** to start the simulation. The level is cleared when every blue objective cell has been reached by a living cell at least once. Press **R** to reset and **Esc** to return to the menu.

### Controls

| Key | Action |
|-----|--------|
| `Space` | Start / pause simulation |
| `R` | Reset level |
| `Esc` | Return to menu |
| `P` | Toggle next-generation preview (births/deaths overlay) |
| `Z` / `Y` | Undo / redo cell placement |
| `T` | Cycle simulation speed (1×, 2×, 4×) |
| `N` | Advance one generation while paused |

## Level Creator

Accessible from the main menu. Paint permanent cells, objective cells, alive cells, and a start zone rectangle directly on the grid. Type a name and press **Enter** to save.

## Project structure

| File | Purpose |
|------|---------|
| `main.py` | Entry point and mode router |
| `game.py` | Game loop, cell placement, simulation, undo/redo |
| `universe.py` | Conway's Game of Life grid and generation transitions |
| `cell.py` | Cell states: dead, alive, permanent, objective |
| `level.py` | Level loading and saving (JSON) |
| `level_creator.py` | In-game level editor |
| `menu.py` | Main menu and level selection |
| `display.py` | Pygame rendering utilities |
| `constants.py` | Window size, grid size, FPS, asset paths |
| `color.py` | Retro color palette |
| `sound.py` | Sound manager (SFX + background music) |
| `levels/` | Bundled level JSON files |
| `assets/` | Font and audio assets |
