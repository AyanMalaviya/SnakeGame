#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local multiplayer gameplay for Snake Rush.

No server, no host/join, and no network setup.
"""

import asyncio
import math
import random
from typing import Optional, Tuple

import pygame

from multiplayer_logic import MultiplayerGameLogic


def get_clockwise_corner_spawns(cols: int, rows: int):
    """Return up to 4 clockwise corner spawns with default facing directions."""
    right = max(1, cols - 2)
    bottom = max(1, rows - 2)
    return [
        ((1, 1), (1, 0)),
        ((right, 1), (0, 1)),
        ((right, bottom), (-1, 0)),
        ((1, bottom), (0, -1)),
    ]


def make_red_snake_assets(cell: int, dir_angle: dict) -> Tuple[dict, pygame.Surface]:
    """Create the alternate head/body assets for Player 2."""
    red_head = pygame.Surface((cell, cell), pygame.SRCALPHA)
    pygame.draw.rect(red_head, (210, 60, 60), (0, 0, cell, cell), border_radius=12)
    pygame.draw.rect(red_head, (160, 30, 30), (cell // 2, 3, cell // 2, cell - 6), border_radius=8)
    pygame.draw.circle(red_head, (240, 240, 240), (cell - 7, 8), 5)
    pygame.draw.circle(red_head, (240, 240, 240), (cell - 7, cell - 8), 5)
    pygame.draw.circle(red_head, (10, 10, 10), (cell - 5, 8), 2)
    pygame.draw.circle(red_head, (10, 10, 10), (cell - 5, cell - 8), 2)

    red_heads = {d: pygame.transform.rotate(red_head, a) for d, a in dir_angle.items()}

    red_body = pygame.Surface((cell, cell), pygame.SRCALPHA)
    pygame.draw.rect(red_body, (200, 50, 50), (1, 1, cell - 2, cell - 2), border_radius=6)
    pygame.draw.rect(red_body, (150, 30, 30), (5, 5, cell - 10, cell - 10), border_radius=4)
    return red_heads, red_body


async def multiplayer_mode(
    player1_name: str,
    player2_name: str,
    difficulty: str,
    w: int,
    h: int,
    cell: int,
) -> Optional[str]:
    """
    Run local 2-player multiplayer mode.

    Controls:
    - Player 1: Arrow keys + Numpad (8/4/2/6)
    - Player 2: WASD + IJKL

    Match rules:
    - Duration: 3 minutes
    - Winner: highest peak length reached during the match
    - No score points in multiplayer mode
    """
    pygame.init()
    screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption("Hizzz Snake - Local Multiplayer")
    clock = pygame.time.Clock()

    # Import required modules and functions from single-player file
    from main import (
        make_head,
        make_body,
        make_tail,
        make_stone,
        SnakeLinkedList,
        DIFFICULTIES,
        DIR_ANGLE,
        interpolate,
        draw_button,
        asset_path,
    )

    # Fonts
    font_names = ["monospace", "dejavu sans mono", "courier new", "consolas"]
    for font_name in font_names:
        try:
            font_lg = pygame.font.SysFont(font_name, max(28, cell + 6), bold=True)
            font_md = pygame.font.SysFont(font_name, max(20, cell), bold=True)
            font_sm = pygame.font.SysFont(font_name, max(14, cell - 6))
            break
        except Exception:
            continue
    else:
        font_lg = pygame.font.Font(None, max(28, cell + 6))
        font_md = pygame.font.Font(None, max(20, cell))
        font_sm = pygame.font.Font(None, max(14, cell - 6))

    cols = w // cell
    top_ui_space = max(58, min(h // 12, cell * 2))
    rows = max(8, (h - top_ui_space) // cell)
    playfield_y = h - (rows * cell)

    # Create sprites
    img_head = make_head(cell)
    img_body = make_body(cell)
    img_tail = make_tail(cell)
    img_stone = make_stone(cell)
    img_apple = pygame.image.load(asset_path("apple.png")).convert_alpha()
    red_heads, red_body = make_red_snake_assets(cell, DIR_ANGLE)

    heads = {d: pygame.transform.rotate(img_head, a) for d, a in DIR_ANGLE.items()}
    tails = {d: pygame.transform.rotate(img_tail, a) for d, a in DIR_ANGLE.items()}

    # Grid surface
    grid_surf = pygame.Surface((w, rows * cell), pygame.SRCALPHA)
    for gx in range(cols):
        for gy in range(rows):
            pygame.draw.circle(grid_surf, (52, 56, 65), (gx * cell + cell // 2, gy * cell + cell // 2), 1)

    cfg = DIFFICULTIES[difficulty]
    speed = cfg["speed"]
    match_duration_sec = 180.0

    # Clockwise corner spawns prepared for future 4-player expansion.
    corner_spawns = get_clockwise_corner_spawns(cols, rows)
    p1_spawn, p1_dir = corner_spawns[0]
    p2_spawn, p2_dir = corner_spawns[1]

    snake_p1 = SnakeLinkedList(*p1_spawn)
    snake_p2 = SnakeLinkedList(*p2_spawn)

    p1_dx, p1_dy = p1_dir
    p1_ndx, p1_ndy = p1_dir
    p1_progress = 0.0
    p1_growth = 0
    p1_peak_len = snake_p1.length
    p1_input_count = 0
    p1_last_apple_input = None

    p2_dx, p2_dy = p2_dir
    p2_ndx, p2_ndy = p2_dir
    p2_progress = 0.0
    p2_growth = 0
    p2_peak_len = snake_p2.length
    p2_input_count = 0
    p2_last_apple_input = None

    spawn_cells = {pos for pos, _ in corner_spawns}

    def random_free_cell() -> Tuple[int, int]:
        blocked = stones | set(snake_p1.get_positions()) | set(snake_p2.get_positions())
        while True:
            x = random.randint(0, cols - 1)
            y = random.randint(0, rows - 1)
            if (x, y) not in blocked:
                return x, y

    stones = set()
    while len(stones) < cfg["stones"]:
        sx, sy = random.randint(0, cols - 1), random.randint(0, rows - 1)
        if (sx, sy) not in spawn_cells:
            stones.add((sx, sy))

    apple_x, apple_y = random_free_cell()

    state = "countdown"
    countdown = 3.0
    time_left = match_duration_sec
    game_over_info = None
    collision_banner = ""
    banner_timer = 0.0

    def set_banner(text: str):
        nonlocal collision_banner, banner_timer
        collision_banner = text
        banner_timer = 1.2

    def queue_p1_direction(next_dx: int, next_dy: int):
        nonlocal p1_ndx, p1_ndy, p1_input_count
        if next_dx == -p1_dx and next_dy == -p1_dy:
            return
        if next_dx == p1_ndx and next_dy == p1_ndy:
            return
        p1_ndx, p1_ndy = next_dx, next_dy
        p1_input_count += 1

    def queue_p2_direction(next_dx: int, next_dy: int):
        nonlocal p2_ndx, p2_ndy, p2_input_count
        if next_dx == -p2_dx and next_dy == -p2_dy:
            return
        if next_dx == p2_ndx and next_dy == p2_ndy:
            return
        p2_ndx, p2_ndy = next_dx, next_dy
        p2_input_count += 1

    while True:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        if banner_timer > 0:
            banner_timer = max(0.0, banner_timer - dt)

        # ==================== EVENTS ====================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"

                if state == "playing":
                    # Player 1 controls: Arrow keys + Numpad 8/4/2/6
                    if event.key in (pygame.K_UP, pygame.K_KP8) and p1_dy != 1:
                        queue_p1_direction(0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_KP2) and p1_dy != -1:
                        queue_p1_direction(0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_KP4) and p1_dx != 1:
                        queue_p1_direction(-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_KP6) and p1_dx != -1:
                        queue_p1_direction(1, 0)

                    # Player 2 controls: WASD + IJKL
                    if event.key in (pygame.K_w, pygame.K_i) and p2_dy != 1:
                        queue_p2_direction(0, -1)
                    elif event.key in (pygame.K_s, pygame.K_k) and p2_dy != -1:
                        queue_p2_direction(0, 1)
                    elif event.key in (pygame.K_a, pygame.K_j) and p2_dx != 1:
                        queue_p2_direction(-1, 0)
                    elif event.key in (pygame.K_d, pygame.K_l) and p2_dx != -1:
                        queue_p2_direction(1, 0)

            if event.type == pygame.MOUSEBUTTONDOWN and state == "game_over":
                mx, my = event.pos
                if w // 2 - 100 <= mx <= w // 2 + 100 and h // 2 + 80 <= my <= h // 2 + 132:
                    return "menu"

        # ==================== COUNTDOWN ====================
        if state == "countdown":
            countdown -= dt
            if countdown <= 0:
                state = "playing"

        # ==================== GAME LOGIC ====================
        elif state == "playing":
            p1_progress += dt * speed
            p2_progress += dt * speed

            prev_p1_head = (snake_p1.head.x, snake_p1.head.y)
            prev_p2_head = (snake_p2.head.x, snake_p2.head.y)

            ate_apple_p1 = False
            ate_apple_p2 = False
            p1_moved = False
            p2_moved = False

            if p1_progress >= 1.0:
                p1_progress -= 1.0
                p1_dx, p1_dy = p1_ndx, p1_ndy
                p1_moved = True

                new_x = (snake_p1.head.x + p1_dx) % cols
                new_y = (snake_p1.head.y + p1_dy) % rows

                if new_x == apple_x and new_y == apple_y:
                    ate_apple_p1 = True
                    p1_growth += 1
                    if p1_last_apple_input is not None and (p1_input_count - p1_last_apple_input) == 1:
                        p1_growth += 1
                        set_banner("P1 APPLE COMBO: +1 EXTRA LENGTH")
                    p1_last_apple_input = p1_input_count

                grow_now = p1_growth > 0
                if grow_now:
                    p1_growth -= 1
                snake_p1.move(new_x, new_y, grow_now)

            if p2_progress >= 1.0:
                p2_progress -= 1.0
                p2_dx, p2_dy = p2_ndx, p2_ndy
                p2_moved = True

                new_x = (snake_p2.head.x + p2_dx) % cols
                new_y = (snake_p2.head.y + p2_dy) % rows

                if new_x == apple_x and new_y == apple_y:
                    ate_apple_p2 = True
                    p2_growth += 1
                    if p2_last_apple_input is not None and (p2_input_count - p2_last_apple_input) == 1:
                        p2_growth += 1
                        set_banner("P2 APPLE COMBO: +1 EXTRA LENGTH")
                    p2_last_apple_input = p2_input_count

                grow_now = p2_growth > 0
                if grow_now:
                    p2_growth -= 1
                snake_p2.move(new_x, new_y, grow_now)

            # Spawn a new apple if any player ate it
            if ate_apple_p1 or ate_apple_p2:
                apple_x, apple_y = random_free_cell()

            # Apply player-vs-player collisions only when at least one snake advanced.
            if p1_moved or p2_moved:
                p1_positions_before = snake_p1.get_positions()
                p2_positions_before = snake_p2.get_positions()

                head_clash = MultiplayerGameLogic.apply_head_collision_halving(snake_p1, snake_p2)

                # Also count a one-tick head swap as a clash.
                if not head_clash and p1_moved and p2_moved:
                    p1_head_now = p1_positions_before[0]
                    p2_head_now = p2_positions_before[0]
                    if p1_head_now == prev_p2_head and p2_head_now == prev_p1_head:
                        MultiplayerGameLogic.trim_snake_to_length(snake_p1, max(1, snake_p1.length // 2))
                        MultiplayerGameLogic.trim_snake_to_length(snake_p2, max(1, snake_p2.length // 2))
                        head_clash = True

                if head_clash:
                    set_banner("HEAD CLASH: BOTH SNAKES HALVED")
                else:
                    p1_head = p1_positions_before[0]
                    p2_head = p2_positions_before[0]

                    p1_hit_idx = MultiplayerGameLogic.get_body_hit_index(p1_head, p2_positions_before)
                    p2_hit_idx = MultiplayerGameLogic.get_body_hit_index(p2_head, p1_positions_before)

                    events = []
                    if p1_hit_idx is not None:
                        removed = MultiplayerGameLogic.trim_snake_to_length(snake_p2, p1_hit_idx)
                        if removed > 0:
                            p1_growth += removed
                            events.append(f"P1 CUT P2 (-{removed})")

                    if p2_hit_idx is not None:
                        removed = MultiplayerGameLogic.trim_snake_to_length(snake_p1, p2_hit_idx)
                        if removed > 0:
                            p2_growth += removed
                            events.append(f"P2 CUT P1 (-{removed})")

                    if events:
                        set_banner(" | ".join(events))

            p1_positions = snake_p1.get_positions()
            p2_positions = snake_p2.get_positions()

            penalty_events = []

            if MultiplayerGameLogic.check_self_collision(p1_positions):
                removed = MultiplayerGameLogic.trim_snake_to_length(snake_p1, max(1, snake_p1.length // 2))
                if removed > 0:
                    penalty_events.append(f"P1 SELF HIT (-{removed})")

            if MultiplayerGameLogic.check_self_collision(p2_positions):
                removed = MultiplayerGameLogic.trim_snake_to_length(snake_p2, max(1, snake_p2.length // 2))
                if removed > 0:
                    penalty_events.append(f"P2 SELF HIT (-{removed})")

            p1_positions = snake_p1.get_positions()
            p2_positions = snake_p2.get_positions()

            if MultiplayerGameLogic.check_stone_collision(p1_positions[0], stones):
                removed = MultiplayerGameLogic.trim_snake_to_length(snake_p1, max(1, snake_p1.length // 2))
                if removed > 0:
                    penalty_events.append(f"P1 STONE HIT (-{removed})")

            if MultiplayerGameLogic.check_stone_collision(p2_positions[0], stones):
                removed = MultiplayerGameLogic.trim_snake_to_length(snake_p2, max(1, snake_p2.length // 2))
                if removed > 0:
                    penalty_events.append(f"P2 STONE HIT (-{removed})")

            if penalty_events:
                set_banner(" | ".join(penalty_events))

            p1_peak_len = max(p1_peak_len, snake_p1.length)
            p2_peak_len = max(p2_peak_len, snake_p2.length)

            time_left = max(0.0, time_left - dt)
            if time_left <= 0.0:
                if p1_peak_len > p2_peak_len:
                    winner = "P1"
                elif p2_peak_len > p1_peak_len:
                    winner = "P2"
                else:
                    winner = "TIE"

                game_over_info = {
                    "winner": winner,
                    "p1_peak": p1_peak_len,
                    "p2_peak": p2_peak_len,
                    "p1_length": snake_p1.length,
                    "p2_length": snake_p2.length,
                }
                state = "game_over"

        # ==================== RENDER ====================
        screen.fill((40, 44, 52))
        pygame.draw.rect(screen, (24, 34, 48), (0, 0, w, playfield_y))
        screen.blit(grid_surf, (0, playfield_y))
        pygame.draw.line(screen, (86, 124, 138), (0, playfield_y), (w, playfield_y), 1)

        for sx, sy in stones:
            screen.blit(img_stone, (sx * cell, playfield_y + sy * cell))

        pulse = 0.05 * math.sin(pygame.time.get_ticks() * 0.005)
        apple_size = int(cell * (1.0 + pulse))
        apple_scaled = pygame.transform.smoothscale(img_apple, (apple_size, apple_size))
        off = (cell - apple_size) // 2
        screen.blit(apple_scaled, (apple_x * cell + off, playfield_y + apple_y * cell + off))

        def render_snake(snake, dx, dy, progress, is_p1=True):
            positions = snake.get_positions()

            if is_p1:
                img_body_use = img_body
                heads_use = heads
            else:
                img_body_use = red_body
                heads_use = red_heads

            nx_head = (positions[0][0] + (1 if dx == 1 else -1 if dx == -1 else 0)) % cols
            ny_head = (positions[0][1] + (1 if dy == 1 else -1 if dy == -1 else 0)) % rows
            next_positions = [(nx_head, ny_head)] + positions[:-1]

            for i, ((cx, cy), (nxt_x, nxt_y)) in enumerate(zip(positions, next_positions)):
                rx, ry = interpolate(cx, cy, nxt_x, nxt_y, progress, cols, rows, cell)
                draw_y = ry + playfield_y
                if i == 0:
                    screen.blit(heads_use.get((dx, dy), img_head), (rx, draw_y))
                elif i == len(positions) - 1:
                    screen.blit(tails.get((dx, dy), img_tail), (rx, draw_y))
                else:
                    screen.blit(img_body_use, (rx, draw_y))

        render_snake(snake_p1, p1_dx, p1_dy, p1_progress, is_p1=True)
        render_snake(snake_p2, p2_dx, p2_dy, p2_progress, is_p1=False)

        # HUD
        hud_p1 = font_sm.render(
            f"P1 ({player1_name}): Len {snake_p1.length} | Peak {p1_peak_len} | Grow +{p1_growth}",
            True,
            (80, 200, 80),
        )
        screen.blit(hud_p1, (10, 10))

        hud_p2 = font_sm.render(
            f"P2 ({player2_name}): Len {snake_p2.length} | Peak {p2_peak_len} | Grow +{p2_growth}",
            True,
            (200, 80, 80),
        )
        screen.blit(hud_p2, (w - hud_p2.get_width() - 10, 10))

        mins = int(time_left) // 60
        secs = int(time_left) % 60
        timer_txt = font_md.render(f"TIME {mins:02d}:{secs:02d}", True, (234, 210, 120))
        screen.blit(timer_txt, (w // 2 - timer_txt.get_width() // 2, 10))

        controls = font_sm.render("P1: Arrow + KP(8,4,2,6)    P2: WASD + IJKL", True, (170, 182, 198))
        controls_y = max(10, playfield_y - controls.get_height() - 6)
        screen.blit(controls, (w // 2 - controls.get_width() // 2, controls_y))

        if banner_timer > 0 and collision_banner:
            banner = font_sm.render(collision_banner, True, (250, 214, 104))
            screen.blit(banner, (w // 2 - banner.get_width() // 2, max(10, controls_y - banner.get_height() - 4)))

        if state == "countdown":
            cd_val = max(0, int(countdown) + 1)
            if cd_val > 0:
                cd_txt = font_lg.render(str(cd_val), True, (200, 200, 100))
            else:
                cd_txt = font_lg.render("GO!", True, (100, 200, 100))
            screen.blit(cd_txt, (w // 2 - cd_txt.get_width() // 2, h // 2 - cd_txt.get_height() // 2))

        if state == "game_over" and game_over_info:
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            if game_over_info["winner"] == "TIE":
                go_txt = font_lg.render("TIE!", True, (200, 200, 100))
            elif game_over_info["winner"] == "P1":
                go_txt = font_lg.render(f"{player1_name.upper()} WINS!", True, (100, 200, 100))
            else:
                go_txt = font_lg.render(f"{player2_name.upper()} WINS!", True, (200, 100, 100))

            screen.blit(go_txt, (w // 2 - go_txt.get_width() // 2, h // 2 - 80))

            score_txt = font_md.render(
                f"P1 Peak: {game_over_info['p1_peak']} (final len {game_over_info['p1_length']})  |  "
                + f"P2 Peak: {game_over_info['p2_peak']} (final len {game_over_info['p2_length']})",
                True,
                (200, 200, 200),
            )
            screen.blit(score_txt, (w // 2 - score_txt.get_width() // 2, h // 2 - 20))

            sub_txt = font_sm.render("Winner is the player with the highest peak length in 3:00", True, (170, 182, 198))
            screen.blit(sub_txt, (w // 2 - sub_txt.get_width() // 2, h // 2 + 12))

            draw_button(screen, w // 2 - 100, h // 2 + 80, 200, 52, (100, 150, 200), alpha=200)
            rematch_txt = font_md.render("BACK TO MENU", True, (255, 255, 255))
            screen.blit(rematch_txt, (w // 2 - rematch_txt.get_width() // 2,
                                      h // 2 + 80 + 26 - rematch_txt.get_height() // 2))

        pygame.display.flip()
        await asyncio.sleep(0)
