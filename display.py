import os
from functools import lru_cache

import pygame

from constants import CELL_SIZE, FONT_NAME, FONT_PATH
import color


@lru_cache(maxsize=128)
def _load_font(size, font_name=FONT_NAME, font_path=FONT_PATH):
    if font_path and os.path.isfile(font_path):
        try:
            return pygame.font.Font(font_path, size)
        except pygame.error:
            pass
    return pygame.font.SysFont(font_name, size)


def _clamp(value):
    return max(0, min(255, int(value)))


def _lighten(rgb, amount):
    return (_clamp(rgb[0] + amount), _clamp(rgb[1] + amount), _clamp(rgb[2] + amount))


def _darken(rgb, amount):
    return (_clamp(rgb[0] - amount), _clamp(rgb[1] - amount), _clamp(rgb[2] - amount))


@lru_cache(maxsize=16)
def _star_points(size):
    width, height = size
    count = max(60, (width * height) // 18000)
    points = []
    for i in range(count):
        x = (i * 73 + i * i * 17) % width
        y = (i * 53 + i * i * 11) % height
        base = 120 + ((i * 19) % 120)
        phase = i % 4
        points.append((x, y, base, phase))
    return tuple(points)


@lru_cache(maxsize=8)
def _scanline_overlay(size):
    width, height = size
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(0, height, 3):
        pygame.draw.line(overlay, color.SCANLINE, (0, y), (width, y))
    return overlay


def draw_retro_background(screen, tick=0):
    width, height = screen.get_size()
    for y in range(height):
        t = y / max(1, height - 1)
        r = color.BG_TOP[0] + (color.BG_BOTTOM[0] - color.BG_TOP[0]) * t
        g = color.BG_TOP[1] + (color.BG_BOTTOM[1] - color.BG_TOP[1]) * t
        b = color.BG_TOP[2] + (color.BG_BOTTOM[2] - color.BG_TOP[2]) * t
        pygame.draw.line(screen, (_clamp(r), _clamp(g), _clamp(b)), (0, y), (width, y))

    twinkle_phase = (tick // 130) % 4
    for x, y, base, phase in _star_points((width, height)):
        sparkle = 70 if (twinkle_phase + phase) % 4 == 0 else 0
        glow = _clamp(base + sparkle)
        screen.set_at((x, y), (glow, glow, glow))

    screen.blit(_scanline_overlay((width, height)), (0, 0))


def draw_panel(
    screen,
    rect,
    fill_color=color.PANEL_BG,
    border_light=color.PANEL_STROKE,
    border_dark=color.PANEL_STROKE_DARK,
):
    pygame.draw.rect(screen, fill_color, rect)
    pygame.draw.rect(screen, border_dark, rect, 4)
    inner = rect.inflate(-6, -6)
    if inner.w > 0 and inner.h > 0:
        pygame.draw.rect(screen, border_light, inner, 2)
    core = rect.inflate(-10, -10)
    if core.w > 0 and core.h > 0:
        pygame.draw.rect(screen, _darken(fill_color, 6), core, 1)
    return rect


def draw_grid(screen, rows, cols, offset_x=0, offset_y=0):
    for r in range(rows + 1):
        y = offset_y + r * CELL_SIZE
        major = r % 5 == 0
        pygame.draw.line(
            screen,
            color.GRID_LINE_BRIGHT if major else color.GRID_LINE,
            (offset_x, y),
            (offset_x + cols * CELL_SIZE, y),
            2 if major else 1,
        )
    for c in range(cols + 1):
        x = offset_x + c * CELL_SIZE
        major = c % 5 == 0
        pygame.draw.line(
            screen,
            color.GRID_LINE_BRIGHT if major else color.GRID_LINE,
            (x, offset_y),
            (x, offset_y + rows * CELL_SIZE),
            2 if major else 1,
        )


def _draw_pixel_tile(screen, rect, tile_color):
    pygame.draw.rect(screen, tile_color, rect)
    if rect.w <= 8 or rect.h <= 8:
        return

    hi = _lighten(tile_color, 34)
    lo = _darken(tile_color, 40)
    pygame.draw.line(screen, hi, (rect.left + 1, rect.top + 1), (rect.right - 2, rect.top + 1), 2)
    pygame.draw.line(screen, hi, (rect.left + 1, rect.top + 1), (rect.left + 1, rect.bottom - 2), 2)
    pygame.draw.line(screen, lo, (rect.left + 1, rect.bottom - 2), (rect.right - 2, rect.bottom - 2), 2)
    pygame.draw.line(screen, lo, (rect.right - 2, rect.top + 1), (rect.right - 2, rect.bottom - 2), 2)


def draw_cell(screen, row, col, cell_color, offset_x=0, offset_y=0):
    rect = pygame.Rect(
        offset_x + col * CELL_SIZE, offset_y + row * CELL_SIZE, CELL_SIZE, CELL_SIZE
    )
    _draw_pixel_tile(screen, rect, cell_color)


def draw_universe(screen, universe, offset_x=0, offset_y=0):
    from cell import ALIVE, PERMANENT, OBJECTIVE

    rows, cols = universe.rows, universe.cols
    grid_rect = pygame.Rect(offset_x, offset_y, cols * CELL_SIZE, rows * CELL_SIZE)
    frame = grid_rect.inflate(10, 10)
    draw_panel(screen, frame)
    pygame.draw.rect(screen, color.GRID_BG, grid_rect)

    for r in range(rows):
        for c in range(cols):
            cell = universe.grid[r][c]
            rect = pygame.Rect(
                offset_x + c * CELL_SIZE,
                offset_y + r * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )
            if cell.state == PERMANENT:
                _draw_pixel_tile(screen, rect, color.PERMANENT)
                core = pygame.Rect(rect.centerx - 2, rect.centery - 2, 4, 4)
                pygame.draw.rect(screen, color.BLACK, core)
            elif cell.state == ALIVE:
                _draw_pixel_tile(screen, rect, color.ALIVE)
            elif cell.state == OBJECTIVE:
                _draw_pixel_tile(screen, rect, color.DEAD)
                ring = rect.inflate(-10, -10)
                if ring.w > 0 and ring.h > 0:
                    pygame.draw.rect(screen, color.OBJECTIVE, ring, 2)
                core = pygame.Rect(rect.centerx - 2, rect.centery - 2, 4, 4)
                pygame.draw.rect(screen, color.OBJECTIVE, core)
            else:
                _draw_pixel_tile(screen, rect, color.DEAD)

    draw_grid(screen, rows, cols, offset_x, offset_y)


def draw_start_zone(screen, zone, offset_x=0, offset_y=0):
    if zone is None:
        return

    r1, c1, r2, c2 = zone
    for r in range(r1, r2):
        for c in range(c1, c2):
            rect = pygame.Rect(
                offset_x + c * CELL_SIZE, offset_y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE
            )
            overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            overlay.fill((*color.START_ZONE, 58))
            screen.blit(overlay, rect)

            if r in (r1, r2 - 1) or c in (c1, c2 - 1):
                pygame.draw.rect(screen, color.START_ZONE_EDGE, rect, 2)



def draw_generation_preview(screen, current_universe, next_universe, offset_x=0, offset_y=0):
    rows, cols = current_universe.rows, current_universe.cols
    for r in range(rows):
        for c in range(cols):
            current_alive = current_universe.grid[r][c].is_alive
            next_alive = next_universe.grid[r][c].is_alive
            if current_alive == next_alive:
                continue

            rect = pygame.Rect(
                offset_x + c * CELL_SIZE,
                offset_y + r * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )
            overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            overlay.fill(color.PREVIEW_BIRTH if next_alive else color.PREVIEW_DEATH)
            screen.blit(overlay, rect)


def draw_text(
    screen,
    text,
    x,
    y,
    size=24,
    text_color=color.TEXT_PRIMARY,
    font_name=FONT_NAME,
    font_path=FONT_PATH,
):
    font = _load_font(size, font_name, font_path)
    shadow = font.render(text, True, color.TEXT_SHADOW)
    screen.blit(shadow, (x + 2, y + 2))
    surface = font.render(text, True, text_color)
    screen.blit(surface, (x, y))


def draw_text_centered(
    screen,
    text,
    cx,
    cy,
    size=24,
    text_color=color.TEXT_PRIMARY,
    font_name=FONT_NAME,
    font_path=FONT_PATH,
):
    font = _load_font(size, font_name, font_path)
    shadow = font.render(text, True, color.TEXT_SHADOW)
    shadow_rect = shadow.get_rect(center=(cx + 2, cy + 2))
    screen.blit(shadow, shadow_rect)
    surface = font.render(text, True, text_color)
    rect = surface.get_rect(center=(cx, cy))
    screen.blit(surface, rect)


def draw_button(
    screen,
    rect,
    text,
    bg=color.BUTTON_WHITE,
    text_color=color.TEXT_PRIMARY,
    font_size=20,
    border_color=color.BUTTON_BORDER,
    border_width=2,
):
    mouse_pos = pygame.mouse.get_pos()
    hovered = rect.collidepoint(mouse_pos)

    fill = _lighten(bg, 18) if hovered else bg
    bevel_hi = _lighten(fill, 42)
    bevel_lo = _darken(fill, 44)

    pygame.draw.rect(screen, color.PANEL_STROKE_DARK, rect)
    inner = rect.inflate(-4, -4)
    pygame.draw.rect(screen, fill, inner)

    pygame.draw.line(
        screen,
        bevel_hi,
        (inner.left + 1, inner.top + 1),
        (inner.right - 1, inner.top + 1),
        2,
    )
    pygame.draw.line(
        screen,
        bevel_hi,
        (inner.left + 1, inner.top + 1),
        (inner.left + 1, inner.bottom - 1),
        2,
    )
    pygame.draw.line(
        screen,
        bevel_lo,
        (inner.left + 1, inner.bottom - 1),
        (inner.right - 1, inner.bottom - 1),
        2,
    )
    pygame.draw.line(
        screen,
        bevel_lo,
        (inner.right - 1, inner.top + 1),
        (inner.right - 1, inner.bottom - 1),
        2,
    )

    pygame.draw.rect(screen, border_color, rect, border_width)

    y_offset = -1 if hovered else 0
    draw_text_centered(
        screen,
        text,
        rect.centerx,
        rect.centery + y_offset,
        font_size,
        text_color,
    )
    return rect
