import pygame
from constants import (
    CELL_SIZE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    SIMULATION_DELAY,
    FPS,
)
from cell import DEAD, ALIVE
from level import Level
import display
import color

MIN_SIM_DELAY = 40
SPEED_FACTORS = (1, 2, 4)
MAX_HISTORY = 1500


class Game:
    def __init__(self, screen, sounds=None):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.sounds = sounds

    def play_level(self, level_name):
        level = Level.load(level_name)
        if self.sounds:
            self.sounds.play_music(level.music_track)

        universe = level.build_universe()
        offset_x = 20
        offset_y = 54
        placing = True
        simulating = False
        paused = False
        won = False
        accumulated_step = 0
        generation_count = 0
        reached_objectives = set()
        preview_enabled = True
        speed_index = 0
        undo_stack = []
        redo_stack = []

        try:
            while True:
                dt = self.clock.tick(FPS)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "quit"
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            if self.sounds:
                                self.sounds.play("ui_back")
                            return "menu"
                        if event.key == pygame.K_SPACE:
                            if placing:
                                placing = False
                                simulating = True
                                paused = False
                                self._update_reached_objectives(
                                    universe, level.objectives, reached_objectives
                                )
                                if (
                                    level.objectives
                                    and len(reached_objectives) == len(level.objectives)
                                ):
                                    won = True
                                    if self.sounds:
                                        self.sounds.play("win")
                                elif self.sounds:
                                    self.sounds.play("sim_start")
                            elif simulating:
                                paused = not paused
                                if self.sounds:
                                    self.sounds.play("pause_toggle")
                        if event.key == pygame.K_p and placing:
                            preview_enabled = not preview_enabled
                            if self.sounds:
                                self.sounds.play("ui_select")
                        if event.key == pygame.K_z and placing and not won:
                            if self._undo_setup_change(universe, undo_stack, redo_stack):
                                if self.sounds:
                                    self.sounds.play("cell_remove")
                        if event.key == pygame.K_y and placing and not won:
                            if self._redo_setup_change(universe, undo_stack, redo_stack):
                                if self.sounds:
                                    self.sounds.play("cell_place")
                        if event.key == pygame.K_t:
                            speed_index = (speed_index + 1) % len(SPEED_FACTORS)
                            if self.sounds:
                                self.sounds.play("ui_select")
                        if event.key == pygame.K_n and simulating and paused and not won:
                            generation_count += 1
                            won = self._advance_generation(
                                universe, level.objectives, reached_objectives
                            )
                            if won and self.sounds:
                                self.sounds.play("win")
                        if event.key == pygame.K_r:
                            universe = level.build_universe()
                            placing = True
                            simulating = False
                            paused = False
                            won = False
                            accumulated_step = 0
                            generation_count = 0
                            reached_objectives.clear()
                            undo_stack.clear()
                            redo_stack.clear()
                            if self.sounds:
                                self.sounds.play("reset")
                    if event.type == pygame.MOUSEBUTTONDOWN and placing and not won:
                        mx, my = event.pos
                        col = (mx - offset_x) // CELL_SIZE
                        row = (my - offset_y) // CELL_SIZE
                        if 0 <= row < universe.rows and 0 <= col < universe.cols:
                            if self._in_start_zone(row, col, level.start_zone):
                                cell = universe.grid[row][col]
                                if cell.state == DEAD:
                                    changed = self._apply_setup_change(
                                        universe,
                                        row,
                                        col,
                                        ALIVE,
                                        undo_stack,
                                        redo_stack,
                                    )
                                    if changed and self.sounds:
                                        self.sounds.play("cell_place")
                                elif cell.state == ALIVE:
                                    changed = self._apply_setup_change(
                                        universe,
                                        row,
                                        col,
                                        DEAD,
                                        undo_stack,
                                        redo_stack,
                                    )
                                    if changed and self.sounds:
                                        self.sounds.play("cell_remove")

                if simulating and not paused and not won:
                    accumulated_step += dt
                    simulation_delay = max(
                        MIN_SIM_DELAY, SIMULATION_DELAY // SPEED_FACTORS[speed_index]
                    )
                    while accumulated_step >= simulation_delay and not won:
                        accumulated_step -= simulation_delay
                        generation_count += 1
                        won = self._advance_generation(
                            universe, level.objectives, reached_objectives
                        )
                        if won and self.sounds:
                            self.sounds.play("win")

                display.draw_retro_background(self.screen, pygame.time.get_ticks())
                display.draw_universe(self.screen, universe, offset_x, offset_y)
                if placing and preview_enabled:
                    next_universe = universe.copy()
                    next_universe.next_generation()
                    display.draw_generation_preview(
                        self.screen, universe, next_universe, offset_x, offset_y
                    )
                if level.start_zone and placing:
                    display.draw_start_zone(
                        self.screen, level.start_zone, offset_x, offset_y
                    )

                objectives_total = len(level.objectives)
                objectives_done = len(reached_objectives)
                status = "SETUP"
                if simulating:
                    status = "PAUSED" if paused else "RUNNING"
                speed_factor = SPEED_FACTORS[speed_index]

                top_panel = pygame.Rect(14, 8, WINDOW_WIDTH - 28, 38)
                display.draw_panel(self.screen, top_panel)
                display.draw_text(
                    self.screen,
                    f"LEVEL: {level.name.upper()}  |  STATUS: {status}  |  SPEED: {speed_factor}X  |  GEN: {generation_count}  |  GOALS: {objectives_done}/{objectives_total}",
                    26,
                    18,
                    10,
                    color.TEXT_PRIMARY,
                )

                bottom_panel = pygame.Rect(14, WINDOW_HEIGHT - 46, WINDOW_WIDTH - 28, 32)
                display.draw_panel(self.screen, bottom_panel)
                if placing:
                    hint = "SETUP: CLICK PLACE/REMOVE  |  Z UNDO  Y REDO  |  P PREVIEW  |  T SPEED  |  SPACE START  |  R RESET  |  ESC MENU"
                    if preview_enabled:
                        display.draw_text(
                            self.screen,
                            "PREVIEW LEGEND: CYAN=BIRTH  RED=DEATH",
                            24,
                            WINDOW_HEIGHT - 58,
                            9,
                            color.TEXT_DARK,
                        )
                elif paused:
                    hint = "PAUSED: SPACE RESUME  |  N SINGLE STEP  |  T SPEED  |  R RESET  |  ESC MENU"
                else:
                    hint = "RUNNING: SPACE PAUSE  |  T SPEED  |  R RESET  |  ESC MENU"
                display.draw_text(
                    self.screen,
                    hint,
                    24,
                    WINDOW_HEIGHT - 38,
                    8,
                    color.TEXT_DARK,
                )

                if won:
                    self._draw_win_screen()

                pygame.display.flip()
        finally:
            if self.sounds:
                self.sounds.stop_music()

    def _in_start_zone(self, row, col, zone):
        if zone is None:
            return True
        r1, c1, r2, c2 = zone
        return r1 <= row < r2 and c1 <= col < c2

    def _advance_generation(self, universe, objectives, reached_objectives):
        universe.next_generation()
        self._update_reached_objectives(universe, objectives, reached_objectives)
        return len(reached_objectives) == len(objectives)

    def _append_history(self, stack, entry):
        stack.append(entry)
        if len(stack) > MAX_HISTORY:
            del stack[0]

    def _apply_setup_change(self, universe, row, col, new_state, undo_stack, redo_stack):
        cell = universe.grid[row][col]
        old_state = cell.state
        if old_state == new_state:
            return False
        if old_state not in (DEAD, ALIVE) or new_state not in (DEAD, ALIVE):
            return False

        cell.state = new_state
        self._append_history(undo_stack, (row, col, old_state, new_state))
        redo_stack.clear()
        return True

    def _undo_setup_change(self, universe, undo_stack, redo_stack):
        if not undo_stack:
            return False
        row, col, old_state, new_state = undo_stack.pop()
        universe.grid[row][col].state = old_state
        self._append_history(redo_stack, (row, col, old_state, new_state))
        return True

    def _redo_setup_change(self, universe, undo_stack, redo_stack):
        if not redo_stack:
            return False
        row, col, old_state, new_state = redo_stack.pop()
        universe.grid[row][col].state = new_state
        self._append_history(undo_stack, (row, col, old_state, new_state))
        return True

    def _update_reached_objectives(self, universe, objectives, reached_objectives):
        for r, c in objectives:
            if universe.grid[r][c].is_alive:
                reached_objectives.add((r, c))

    def _draw_win_screen(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill(color.LEVEL_PASSED_BG)
        self.screen.blit(overlay, (0, 0))

        win_rect = pygame.Rect(
            WINDOW_WIDTH // 2 - 250, WINDOW_HEIGHT // 2 - 110, 500, 220
        )
        display.draw_panel(self.screen, win_rect)

        display.draw_text_centered(
            self.screen,
            "LEVEL CLEARED",
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 - 34,
            36,
            color.TEXT_ACCENT,
        )
        display.draw_text_centered(
            self.screen,
            "PRESS ESC TO RETURN",
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 + 30,
            14,
            color.TEXT_PRIMARY,
        )
