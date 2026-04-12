#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Linked List Snake - Multiplayer Integration
Extended version of main.py with multiplayer support
Run this instead of main.py for multiplayer capability

This script automatically starts an embedded multiplayer server in the background,
so users only need to launch one executable for both single-player and multiplayer modes.
"""

import pygame
import random
import sys
import math
import asyncio
import os
import threading
import time
from multiplayer_client import MultiplayerClient
from multiplayer_ui import MultiplayerManager, multiplayer_mode
from multiplayer_server import MultiplayerServer

# Import everything from original main.py
try:
    # Import all necessary components (simulated here)
    from main import (
        Node, SnakeLinkedList, make_head, make_body, make_tail, make_stone, make_apple,
        interpolate, asset_path, DIR_ANGLE, DIFFICULTIES, DIFF_KEYS,
        get_dpad_rects, draw_dpad, hit_dpad, draw_button, draw_pause_icon_button, main
    )
except ImportError:
    print("Error: Could not import from main.py")
    sys.exit(1)


# ==================== EMBEDDED MULTIPLAYER SERVER ====================
class EmbeddedServerManager:
    """Manages an embedded multiplayer server running in a background thread"""
    
    def __init__(self, host='127.0.0.1', port=9999):
        self.server = None
        self.host = host
        self.port = port
        self.thread = None
        self.running = False
    
    def start(self):
        """Start the server in a background thread"""
        if self.running:
            return True
        
        try:
            self.server = MultiplayerServer(self.host, self.port)
            self.running = True
            self.thread = threading.Thread(target=self._run_server, daemon=True)
            self.thread.start()
            time.sleep(0.5)  # Give server time to start
            return True
        except Exception as e:
            print(f"Error starting embedded server: {e}")
            self.running = False
            return False
    
    def _run_server(self):
        """Run the server (internal - runs in thread)"""
        try:
            self.server.start()
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.running = False
    
    def stop(self):
        """Stop the server gracefully"""
        if self.running and self.server:
            self.server.shutdown()
            self.running = False
            # Wait briefly for thread to finish
            if self.thread:
                self.thread.join(timeout=2)


# Global server manager
_server_manager = None


async def game_mode_selector(screen_width: int, screen_height: int) -> str:
    """
    Show game mode selection screen
    Returns: "single", "multiplayer_host", "multiplayer_join", or "exit"
    """
    pygame.init()
    info = pygame.display.Info()
    W = info.current_w
    H = info.current_h
    screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption("Linked List Snake - Mode Selection")
    clock = pygame.time.Clock()
    FPS = 60

    CELL = max(min(W // 28, H // 22), 18)
    font_lg = pygame.font.SysFont("monospace", max(28, CELL + 6), bold=True)
    font_md = pygame.font.SysFont("monospace", max(20, CELL), bold=True)
    font_sm = pygame.font.SysFont("monospace", max(14, CELL - 6))

    selected = 0
    modes = ["SINGLE PLAYER", "MULTIPLAYER HOST", "MULTIPLAYER JOIN"]

    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected = (selected - 1) % 3
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    selected = (selected + 1) % 3
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if selected == 0:
                        return "single"
                    elif selected == 1:
                        return "multiplayer_host"
                    else:
                        return "multiplayer_join"
                elif event.key == pygame.K_1:
                    return "single"
                elif event.key == pygame.K_2:
                    return "multiplayer_host"
                elif event.key == pygame.K_3:
                    return "multiplayer_join"
                elif event.key == pygame.K_ESCAPE:
                    return "exit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                button_height = 80
                start_y = H // 2 - button_height
                for i in range(3):
                    y = start_y + i * (button_height + 20)
                    if W // 2 - 150 <= mx <= W // 2 + 150 and y <= my <= y + button_height:
                        selected = i
                        return ["single", "multiplayer_host", "multiplayer_join"][i]

        # Render
        screen.fill((20, 22, 30))

        title = font_lg.render("LINKED LIST SNAKE", True, (60, 210, 60))
        screen.blit(title, (W // 2 - title.get_width() // 2, H // 4))

        subtitle = font_md.render("Select Mode", True, (140, 150, 165))
        screen.blit(subtitle, (W // 2 - subtitle.get_width() // 2, H // 4 + 60))

        # Buttons
        button_width = 300
        button_height = 80
        button_gap = 20
        start_y = H // 2 - button_height

        for i, mode in enumerate(modes):
            y = start_y + i * (button_height + button_gap)
            x = W // 2 - button_width // 2
            is_selected = (i == selected)

            color = (60, 210, 60) if is_selected else (80, 160, 80) if i == 0 else (100, 100, 200) if i == 1 else (200, 100, 100)
            pygame.draw.rect(screen, color, (x, y, button_width, button_height), border_radius=15)

            if is_selected:
                pygame.draw.rect(screen, (255, 255, 255), (x, y, button_width, button_height), 4, border_radius=15)

            text = font_md.render(mode, True, (255, 255, 255))
            screen.blit(text, (x + button_width // 2 - text.get_width() // 2,
                               y + button_height // 2 - text.get_height() // 2))

        help_text = font_sm.render("Arrow Keys or 1/2/3 | ESC to Exit", True, (100, 100, 100))
        screen.blit(help_text, (W // 2 - help_text.get_width() // 2, H - 50))

        pygame.display.flip()
        await asyncio.sleep(0)


async def multiplayer_setup(mode: str) -> tuple:
    """
    Handle multiplayer setup (host or join)
    Returns: (client, session_id, nickname, difficulty) or None if cancelled
    """
    pygame.init()
    info = pygame.display.Info()
    W = info.current_w
    H = info.current_h
    screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption("Linked List Snake - Multiplayer Setup")
    clock = pygame.time.Clock()
    FPS = 60

    CELL = max(min(W // 28, H // 22), 18)
    font_lg = pygame.font.SysFont("monospace", max(28, CELL + 6), bold=True)
    font_md = pygame.font.SysFont("monospace", max(20, CELL), bold=True)
    font_sm = pygame.font.SysFont("monospace", max(14, CELL - 6))

    # Input fields
    nickname = ""
    selected_difficulty = "medium"
    input_field = "nickname"
    status = ""
    client = None

    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if client:
                        client.disconnect()
                    return None

                elif event.key == pygame.K_RETURN:
                    if not nickname:
                        status = "Enter nickname first!"
                    else:
                        # Connect to server and create/join session
                        if not client:
                            client = MultiplayerClient()
                            if not client.connect('localhost', 9999):
                                status = "Cannot connect to server!"
                                client = None
                                continue

                        if mode == "multiplayer_host":
                            session_id = client.create_session(nickname, selected_difficulty)
                            if session_id:
                                return (client, session_id, nickname, selected_difficulty)
                            else:
                                status = "Failed to create session"
                        else:
                            # Show session list for join
                            sessions = client.list_sessions()
                            if sessions:
                                # For now, join first available
                                session_id = sessions[0]['session_id']
                                if client.join_session(session_id, nickname):
                                    return (client, session_id, nickname, selected_difficulty)
                                else:
                                    status = "Failed to join session"
                            else:
                                status = "No available sessions"

                elif event.key == pygame.K_TAB:
                    input_field = "difficulty" if input_field == "nickname" else "nickname"

                elif event.key == pygame.K_BACKSPACE:
                    if input_field == "nickname":
                        nickname = nickname[:-1]

                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if input_field == "difficulty":
                        idx = ["easy", "medium", "hard"].index(selected_difficulty)
                        selected_difficulty = ["easy", "medium", "hard"][(idx - 1) % 3]

                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if input_field == "difficulty":
                        idx = ["easy", "medium", "hard"].index(selected_difficulty)
                        selected_difficulty = ["easy", "medium", "hard"][(idx + 1) % 3]

                elif event.unicode.isprintable() and input_field == "nickname" and len(nickname) < 20:
                    nickname += event.unicode

        # Render
        screen.fill((20, 22, 30))

        title = font_lg.render("MULTIPLAYER SETUP", True, (60, 210, 60))
        screen.blit(title, (W // 2 - title.get_width() // 2, H // 4))

        mode_text = "HOST A GAME" if mode == "multiplayer_host" else "JOIN A GAME"
        mode_render = font_md.render(mode_text, True, (140, 150, 165))
        screen.blit(mode_render, (W // 2 - mode_render.get_width() // 2, H // 4 + 60))

        # Nickname input
        nickname_label = font_md.render("Nickname:", True, (200, 200, 200))
        screen.blit(nickname_label, (W // 4, H // 2 - 40))
        nickname_box = pygame.Rect(W // 4 + 200, H // 2 - 50, 300, 50)
        pygame.draw.rect(screen, (60, 60, 80), nickname_box, border_radius=10)
        if input_field == "nickname":
            pygame.draw.rect(screen, (100, 200, 100), nickname_box, 3, border_radius=10)
        nickname_text = font_sm.render(nickname + ("|" if input_field == "nickname" else ""), True, (255, 255, 255))
        screen.blit(nickname_text, (nickname_box.x + 10, nickname_box.y + 15))

        # Difficulty selection
        difficulty_label = font_md.render("Difficulty:", True, (200, 200, 200))
        screen.blit(difficulty_label, (W // 4, H // 2 + 40))
        for i, diff in enumerate(["easy", "medium", "hard"]):
            x = W // 4 + 200 + i * 120
            y = H // 2 + 30
            color = (60, 210, 60) if diff == selected_difficulty else (80, 100, 150)
            if input_field == "difficulty" and diff == selected_difficulty:
                pygame.draw.rect(screen, (100, 200, 100), (x, y, 100, 40), 3, border_radius=8)
            diff_text = font_sm.render(diff.upper(), True, color)
            screen.blit(diff_text, (x + 50 - diff_text.get_width() // 2, y + 20 - diff_text.get_height() // 2))

        # Status
        if status:
            status_text = font_sm.render(status, True, (220, 60, 60))
            screen.blit(status_text, (W // 2 - status_text.get_width() // 2, H - 100))

        help_text = font_sm.render("TAB: Switch | Arrow Keys: Difficulty | ENTER: Continue | ESC: Back", True, (100, 100, 100))
        screen.blit(help_text, (W // 2 - help_text.get_width() // 2, H - 50))

        pygame.display.flip()
        await asyncio.sleep(0)


async def main_with_multiplayer():
    """
    Main game loop with multiplayer support
    Automatically starts an embedded multiplayer server
    """
    global _server_manager
    
    pygame.init()
    
    # Start embedded multiplayer server
    _server_manager = EmbeddedServerManager('127.0.0.1', 9999)
    if not _server_manager.start():
        print("Warning: Could not start multiplayer server. Multiplayer mode may not work.")
    else:
        print("✓ Multiplayer server started on 127.0.0.1:9999")
    
    try:
        while True:
            # Show mode selector
            mode = await game_mode_selector(1920, 1080)

            if mode == "exit":
                pygame.quit()
                sys.exit()

            elif mode == "single":
                # Run single player game
                await main()

            elif mode in ("multiplayer_host", "multiplayer_join"):
                # Setup multiplayer
                result = await multiplayer_setup(mode)
                if result:
                    client, session_id, nickname, difficulty = result
                    # Run multiplayer game
                    await multiplayer_mode(client, mode == "multiplayer_host", nickname, difficulty, 1920, 1080, 40)
    
    finally:
        # Ensure server is stopped when exiting
        if _server_manager and _server_manager.running:
            _server_manager.stop()
            print("✓ Multiplayer server shut down")


if __name__ == "__main__":
    asyncio.run(main_with_multiplayer())
