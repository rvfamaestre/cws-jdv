import pygame
from constants import CELL_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT
from cell import DEAD, ALIVE, PERMANENT, OBJECTIVE
from level import Level
from universe import Universe
import display
import color


PANEL_X = WINDOW_WIDTH - 250


class LevelCreator:
    def __init__(self, screen, sounds=None):
        self.screen = screen
        self.sounds = sounds
        self.rows = 18
        self.cols = 22
        self.offset_x = 20
        self.offset_y = 54
        self.universe = Universe(self.rows, self.cols)
        self.objectives = []
        self.permanents = []
        self.start_zone = None
        self.mode = "permanent"  # permanent | alive | objective | start
        self.level_name = "My level"
        self.text_active = False
        self.name_rect = pygame.Rect(PANEL_X + 24, 370, 200, 42)
        self.defining_start = False
        self.start_corner = None
        self.running = True

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            self._handle_events()
            self._draw()
            clock.tick(30)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.sounds:
                        self.sounds.play("ui_back")
                    self.running = False
                elif event.key == pygame.K_RETURN:
                    self._save_level()
                    if self.sounds:
                        self.sounds.play("save")
                    self.running = False
                elif self.text_active:
                    if event.key == pygame.K_BACKSPACE:
                        self.level_name = self.level_name[:-1]
                    else:
                        ch = event.unicode
                        if ch.isprintable() and len(self.level_name) < 20:
                            self.level_name += ch
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_click(event.pos)

    def _handle_click(self, pos):
        mx, my = pos
        if mx >= PANEL_X:
            if self.name_rect.collidepoint(mx, my):
                self.text_active = True
                if self.sounds:
                    self.sounds.play("ui_select")
                return

            self.text_active = False
            self._check_buttons(mx, my)
            return

        self.text_active = False
        col = (mx - self.offset_x) // CELL_SIZE
        row = (my - self.offset_y) // CELL_SIZE
        if 0 <= row < self.rows and 0 <= col < self.cols:
            if self.mode == "start":
                self._handle_start_click(row, col)
            else:
                self._toggle_cell(row, col)

    def _handle_start_click(self, row, col):
        if self.start_corner is None:
            self.start_corner = (row, col)
            if self.sounds:
                self.sounds.play("cell_place")
        else:
            r1 = min(self.start_corner[0], row)
            c1 = min(self.start_corner[1], col)
            r2 = max(self.start_corner[0], row) + 1
            c2 = max(self.start_corner[1], col) + 1
            self.start_zone = (r1, c1, r2, c2)
            self.start_corner = None
            self.defining_start = False
            if self.sounds:
                self.sounds.play("zone_set")

    def _toggle_cell(self, row, col):
        cell = self.universe.grid[row][col]
        state_map = {"permanent": PERMANENT, "alive": ALIVE, "objective": OBJECTIVE}
        target = state_map.get(self.mode, DEAD)
        if cell.state == target:
            cell.state = DEAD
            self._remove_tracking(row, col)
            if self.sounds:
                self.sounds.play("cell_remove")
        else:
            self._remove_tracking(row, col)
            cell.state = target
            if target == PERMANENT:
                self.permanents.append((row, col))
            elif target == OBJECTIVE:
                self.objectives.append((row, col))
            if self.sounds:
                self.sounds.play("cell_place")

    def _remove_tracking(self, row, col):
        self.permanents = [(r, c) for r, c in self.permanents if (r, c) != (row, col)]
        self.objectives = [(r, c) for r, c in self.objectives if (r, c) != (row, col)]

    def _check_buttons(self, mx, my):
        for rect, mode in self._get_buttons():
            if rect.collidepoint(mx, my):
                if mode == "start":
                    self.mode = "start"
                    self.defining_start = True
                    self.start_corner = None
                else:
                    self.mode = mode
                if self.sounds:
                    self.sounds.play("ui_select")
                return

    def _get_buttons(self):
        bw, bh = 200, 42
        x = PANEL_X + 24
        return [
            (pygame.Rect(x, 130, bw, bh), "permanent"),
            (pygame.Rect(x, 184, bw, bh), "alive"),
            (pygame.Rect(x, 238, bw, bh), "start"),
            (pygame.Rect(x, 292, bw, bh), "objective"),
        ]

    def _draw(self):
        display.draw_retro_background(self.screen, pygame.time.get_ticks())
        display.draw_universe(self.screen, self.universe, self.offset_x, self.offset_y)

        if self.start_zone:
            display.draw_start_zone(
                self.screen, self.start_zone, self.offset_x, self.offset_y
            )

        top_panel = pygame.Rect(14, 8, WINDOW_WIDTH - 28, 38)
        display.draw_panel(self.screen, top_panel)
        display.draw_text(
            self.screen,
            f"LEVEL CREATOR  |  MODE: {self.mode.upper()}  |  ENTER SAVE  |  ESC BACK",
            24,
            18,
            12,
            color.TEXT_PRIMARY,
        )

        side_panel = pygame.Rect(PANEL_X, 54, WINDOW_WIDTH - PANEL_X - 14, WINDOW_HEIGHT - 70)
        display.draw_panel(self.screen, side_panel)

        display.draw_text_centered(
            self.screen,
            "TOOLS",
            side_panel.centerx,
            94,
            16,
            color.TEXT_ACCENT,
        )

        label_map = {
            "permanent": "PERMANENT",
            "alive": "ALIVE",
            "start": "START ZONE",
            "objective": "OBJECTIVE",
        }
        btn_colors = {
            "permanent": color.BUTTON_RED,
            "alive": color.BUTTON_GREEN,
            "start": color.BUTTON_WHITE,
            "objective": color.BUTTON_BLUE,
        }

        for rect, mode in self._get_buttons():
            bg = btn_colors.get(mode, color.BUTTON_WHITE)
            border = color.TEXT_ACCENT if mode == self.mode else color.BUTTON_BORDER
            display.draw_button(
                self.screen,
                rect,
                label_map.get(mode, mode.upper()),
                bg=bg,
                text_color=color.BLACK if mode == "start" else color.WHITE,
                font_size=12,
                border_color=border,
                border_width=3 if mode == self.mode else 2,
            )

        display.draw_text_centered(
            self.screen,
            "LEVEL NAME",
            side_panel.centerx,
            self.name_rect.y - 12,
            10,
            color.TEXT_DARK,
        )

        name_border = color.TEXT_ACCENT if self.text_active else color.BUTTON_BORDER
        pygame.draw.rect(self.screen, color.PANEL_STROKE_DARK, self.name_rect)
        inner_rect = self.name_rect.inflate(-4, -4)
        pygame.draw.rect(self.screen, color.DARK, inner_rect)
        pygame.draw.rect(self.screen, name_border, self.name_rect, 2)

        name_text = self.level_name if self.level_name else "Type level name"
        name_color = color.TEXT_PRIMARY if self.level_name else color.TEXT_DARK
        display.draw_text(
            self.screen,
            name_text,
            self.name_rect.x + 8,
            self.name_rect.y + 12,
            10,
            name_color,
        )

        if self.text_active and (pygame.time.get_ticks() // 400) % 2 == 0:
            cursor_x = self.name_rect.x + 8 + min(len(self.level_name), 20) * 8
            cursor_top = self.name_rect.y + 10
            cursor_bottom = self.name_rect.y + 30
            pygame.draw.line(
                self.screen,
                color.TEXT_ACCENT,
                (cursor_x, cursor_top),
                (cursor_x, cursor_bottom),
                2,
            )

        display.draw_text_centered(
            self.screen,
            "CLICK GRID TO PAINT CELLS",
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT - 36,
            11,
            color.TEXT_DARK,
        )

        pygame.display.flip()

    def _save_level(self):
        name = self.level_name.strip() if self.level_name.strip() else "untitled_level"
        lvl = Level(name, self.rows, self.cols)
        lvl.permanents = list(self.permanents)
        lvl.objectives = list(self.objectives)
        lvl.start_zone = self.start_zone

        alive = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.universe.grid[r][c].state == ALIVE:
                    alive.append((r, c))
        lvl.alive_cells = alive
        lvl.save()
