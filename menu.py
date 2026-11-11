import pygame
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, TITLE
from level import Level
import display
import color


class Menu:
    def __init__(self, screen, sounds=None):
        self.screen = screen
        self.sounds = sounds
        self.selection = None  # will be set to a result string

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.selection = "quit"
                    return self.selection
                if event.type == pygame.MOUSEBUTTONDOWN:
                    result = self._check_click(event.pos)
                    if result:
                        self.selection = result
                        return self.selection
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.sounds:
                        self.sounds.play("ui_back")
                    self.selection = "quit"
                    return self.selection

            self._draw()
            clock.tick(30)

    def _draw(self):
        display.draw_retro_background(self.screen, pygame.time.get_ticks())

        panel_rect = pygame.Rect(WINDOW_WIDTH // 2 - 245, 30, 490, WINDOW_HEIGHT - 60)
        display.draw_panel(self.screen, panel_rect)

        display.draw_text_centered(
            self.screen,
            TITLE,
            WINDOW_WIDTH // 2,
            92,
            40,
            color.TEXT_ACCENT,
        )
        display.draw_text_centered(
            self.screen,
            "CONWAY PUZZLE ARCADE",
            WINDOW_WIDTH // 2,
            132,
            14,
            color.TEXT_DARK,
        )
        display.draw_text_centered(
            self.screen,
            "SELECT A LEVEL",
            WINDOW_WIDTH // 2,
            182,
            16,
            color.TEXT_PRIMARY,
        )

        levels = sorted(Level.list_levels())
        y_start = 215
        self._level_rects = []
        for i, name in enumerate(levels):
            rect = pygame.Rect(WINDOW_WIDTH // 2 - 170, y_start + i * 55, 340, 44)
            display.draw_button(
                self.screen,
                rect,
                name.upper(),
                bg=color.BUTTON_GREEN,
                text_color=color.WHITE,
                font_size=16,
                border_color=color.BUTTON_BORDER,
            )
            self._level_rects.append((rect, name))

        y_creator = y_start + len(levels) * 55 + 25
        self._creator_rect = pygame.Rect(WINDOW_WIDTH // 2 - 170, y_creator, 340, 44)
        display.draw_button(
            self.screen,
            self._creator_rect,
            "LEVEL CREATOR",
            bg=color.BUTTON_BLUE,
            text_color=color.WHITE,
            font_size=16,
            border_color=color.BUTTON_BORDER,
        )

        self._quit_rect = pygame.Rect(WINDOW_WIDTH // 2 - 170, y_creator + 55, 340, 44)
        display.draw_button(
            self.screen,
            self._quit_rect,
            "QUIT",
            bg=color.BUTTON_RED,
            text_color=color.WHITE,
            font_size=16,
            border_color=color.BUTTON_BORDER,
        )

        display.draw_text_centered(
            self.screen,
            "MOUSE TO SELECT  |  ESC TO EXIT",
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT - 38,
            12,
            color.TEXT_DARK,
        )

        pygame.display.flip()

    def _check_click(self, pos):
        for rect, name in self._level_rects:
            if rect.collidepoint(pos):
                if self.sounds:
                    self.sounds.play("ui_select")
                return f"level:{name}"
        if self._creator_rect.collidepoint(pos):
            if self.sounds:
                self.sounds.play("ui_select")
            return "creator"
        if self._quit_rect.collidepoint(pos):
            if self.sounds:
                self.sounds.play("ui_back")
            return "quit"
        return None
