#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Snake Rush - Local Multiplayer Launcher

This launcher keeps the project focused on EXE/Android/Linux builds without
network hosting requirements.
"""

import pygame
import sys
import asyncio
from multiplayer_ui import multiplayer_mode

# Import single-player game entry point
try:
    from main import main
except ImportError:
    print("Error: Could not import main() from main.py")
    sys.exit(1)


async def game_mode_selector(screen_width: int, screen_height: int) -> str:
    """Return one of: single, local_multiplayer, exit."""
    pygame.init()
    info = pygame.display.Info()
    w = info.current_w
    h = info.current_h
    screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption("Hizzz Snake - Mode Selection")
    clock = pygame.time.Clock()

    cell = max(min(w // 28, h // 22), 18)
    font_lg = pygame.font.SysFont("monospace", max(28, cell + 6), bold=True)
    font_md = pygame.font.SysFont("monospace", max(20, cell), bold=True)
    font_sm = pygame.font.SysFont("monospace", max(14, cell - 6))

    selected = 0
    modes = ["SINGLE PLAYER", "LOCAL MULTIPLAYER"]

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(modes)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(modes)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return "single" if selected == 0 else "local_multiplayer"
                elif event.key == pygame.K_1:
                    return "single"
                elif event.key == pygame.K_2:
                    return "local_multiplayer"
                elif event.key == pygame.K_ESCAPE:
                    return "exit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                button_w = 340
                button_h = 86
                gap = 24
                start_y = h // 2 - button_h
                for i in range(len(modes)):
                    y = start_y + i * (button_h + gap)
                    x = w // 2 - button_w // 2
                    if x <= mx <= x + button_w and y <= my <= y + button_h:
                        return "single" if i == 0 else "local_multiplayer"

        # Render
        screen.fill((20, 22, 30))

        title = font_lg.render("HIZZZ", True, (60, 210, 60))
        screen.blit(title, (w // 2 - title.get_width() // 2, h // 4))

        subtitle = font_md.render("Choose Game Mode", True, (170, 190, 212))
        screen.blit(subtitle, (w // 2 - subtitle.get_width() // 2, h // 4 + 60))

        button_w = 340
        button_h = 86
        gap = 24
        start_y = h // 2 - button_h

        for i, mode in enumerate(modes):
            y = start_y + i * (button_h + gap)
            x = w // 2 - button_w // 2
            is_selected = (i == selected)

            if i == 0:
                color = (72, 165, 92) if not is_selected else (88, 210, 112)
            else:
                color = (70, 116, 210) if not is_selected else (90, 140, 245)

            pygame.draw.rect(screen, color, (x, y, button_w, button_h), border_radius=15)
            if is_selected:
                pygame.draw.rect(screen, (255, 255, 255), (x, y, button_w, button_h), 4, border_radius=15)

            text = font_md.render(mode, True, (255, 255, 255))
            screen.blit(text, (x + button_w // 2 - text.get_width() // 2,
                               y + button_h // 2 - text.get_height() // 2))

        help_text = font_sm.render("Arrow Keys or 1/2 | Enter to select | ESC to Exit", True, (120, 132, 150))
        screen.blit(help_text, (w // 2 - help_text.get_width() // 2, h - 50))

        pygame.display.flip()
        await asyncio.sleep(0)


async def local_multiplayer_setup() -> tuple:
    """Collect local multiplayer settings: P1 name, P2 name, difficulty."""
    pygame.init()
    info = pygame.display.Info()
    w = info.current_w
    h = info.current_h
    screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption("Hizzz Snake - Local Multiplayer Setup")
    clock = pygame.time.Clock()

    cell = max(min(w // 28, h // 22), 18)
    font_lg = pygame.font.SysFont("monospace", max(28, cell + 6), bold=True)
    font_md = pygame.font.SysFont("monospace", max(20, cell), bold=True)
    font_sm = pygame.font.SysFont("monospace", max(14, cell - 6))

    player1_name = "Player 1"
    player2_name = "Player 2"
    selected_difficulty = "medium"
    active_field = 0  # 0=p1, 1=p2, 2=difficulty
    status = ""

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None

                elif event.key == pygame.K_TAB:
                    active_field = (active_field + 1) % 3

                elif event.key == pygame.K_RETURN:
                    p1 = player1_name.strip() or "Player 1"
                    p2 = player2_name.strip() or "Player 2"
                    if p1.lower() == p2.lower():
                        status = "Player names must be different"
                    else:
                        return (p1, p2, selected_difficulty)

                elif event.key == pygame.K_BACKSPACE:
                    if active_field == 0:
                        player1_name = player1_name[:-1]
                    elif active_field == 1:
                        player2_name = player2_name[:-1]

                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if active_field == 2:
                        idx = ["easy", "medium", "hard"].index(selected_difficulty)
                        selected_difficulty = ["easy", "medium", "hard"][(idx - 1) % 3]

                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if active_field == 2:
                        idx = ["easy", "medium", "hard"].index(selected_difficulty)
                        selected_difficulty = ["easy", "medium", "hard"][(idx + 1) % 3]

                elif event.unicode.isprintable():
                    if active_field == 0 and len(player1_name) < 20:
                        player1_name += event.unicode
                    elif active_field == 1 and len(player2_name) < 20:
                        player2_name += event.unicode

        # Render
        screen.fill((20, 22, 30))

        title = font_lg.render("LOCAL MULTIPLAYER", True, (60, 210, 60))
        screen.blit(title, (w // 2 - title.get_width() // 2, h // 4))

        sub = font_sm.render("No hosting needed - both players play on this device", True, (165, 178, 196))
        screen.blit(sub, (w // 2 - sub.get_width() // 2, h // 4 + 56))

        control_sub = font_sm.render("P1: Arrow + Numpad(8/4/2/6) | P2: WASD + IJKL", True, (145, 160, 180))
        screen.blit(control_sub, (w // 2 - control_sub.get_width() // 2, h // 4 + 84))

        rule_sub = font_sm.render("3:00 match | Winner = highest peak length", True, (145, 160, 180))
        screen.blit(rule_sub, (w // 2 - rule_sub.get_width() // 2, h // 4 + 108))

        # Player 1 input
        p1_label = font_md.render("Player 1 Name:", True, (210, 210, 210))
        screen.blit(p1_label, (w // 4, h // 2 - 70))
        p1_box = pygame.Rect(w // 4 + 240, h // 2 - 80, 340, 52)
        pygame.draw.rect(screen, (60, 60, 80), p1_box, border_radius=10)
        if active_field == 0:
            pygame.draw.rect(screen, (100, 200, 100), p1_box, 3, border_radius=10)
        p1_text = font_sm.render(player1_name + ("|" if active_field == 0 else ""), True, (255, 255, 255))
        screen.blit(p1_text, (p1_box.x + 10, p1_box.y + 15))

        # Player 2 input
        p2_label = font_md.render("Player 2 Name:", True, (210, 210, 210))
        screen.blit(p2_label, (w // 4, h // 2 + 6))
        p2_box = pygame.Rect(w // 4 + 240, h // 2 - 4, 340, 52)
        pygame.draw.rect(screen, (60, 60, 80), p2_box, border_radius=10)
        if active_field == 1:
            pygame.draw.rect(screen, (100, 200, 100), p2_box, 3, border_radius=10)
        p2_text = font_sm.render(player2_name + ("|" if active_field == 1 else ""), True, (255, 255, 255))
        screen.blit(p2_text, (p2_box.x + 10, p2_box.y + 15))

        # Difficulty selection
        diff_label = font_md.render("Difficulty:", True, (210, 210, 210))
        screen.blit(diff_label, (w // 4, h // 2 + 84))

        for i, diff in enumerate(["easy", "medium", "hard"]):
            x = w // 4 + 240 + i * 126
            y = h // 2 + 78
            color = (60, 210, 60) if diff == selected_difficulty else (80, 100, 150)
            rect = pygame.Rect(x, y, 110, 42)
            if active_field == 2 and diff == selected_difficulty:
                pygame.draw.rect(screen, (100, 200, 100), rect, 3, border_radius=8)
            diff_text = font_sm.render(diff.upper(), True, color)
            screen.blit(diff_text, (x + 55 - diff_text.get_width() // 2, y + 21 - diff_text.get_height() // 2))

        if status:
            status_text = font_sm.render(status, True, (220, 60, 60))
            screen.blit(status_text, (w // 2 - status_text.get_width() // 2, h - 104))

        help_text = font_sm.render(
            "TAB: Switch Field | Arrow Left/Right: Difficulty | ENTER: Start Match | ESC: Back",
            True,
            (110, 120, 136),
        )
        screen.blit(help_text, (w // 2 - help_text.get_width() // 2, h - 54))

        pygame.display.flip()
        await asyncio.sleep(0)


async def main_with_multiplayer():
    """Main launcher loop for single-player and local multiplayer."""
    pygame.init()

    while True:
        mode = await game_mode_selector(1920, 1080)

        if mode == "exit":
            pygame.quit()
            sys.exit()

        if mode == "single":
            await main()
            continue

        if mode == "local_multiplayer":
            result = await local_multiplayer_setup()
            if result:
                p1_name, p2_name, difficulty = result
                await multiplayer_mode(p1_name, p2_name, difficulty, 1920, 1080, 40)


if __name__ == "__main__":
    asyncio.run(main_with_multiplayer())
