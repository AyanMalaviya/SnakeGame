#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multiplayer Game Mode Extension for Linked List Snake
Handles UI, menu selection, and multiplayer game integration
"""

import pygame
import random
import asyncio
import math
from typing import Tuple, Optional, Dict
from multiplayer_client import MultiplayerClient
from multiplayer_logic import MultiplayerGameLogic

class MultiplayerManager:
    """Manages multiplayer game modes and UI"""

    def __init__(self, width: int, height: int, cell_size: int):
        self.W = width
        self.H = height
        self.CELL = cell_size
        self.COLS = width // cell_size
        self.ROWS = height // cell_size

        self.client = None
        self.session_id = None
        self.mode = None  # "host" or "join"
        self.nickname = ""
        self.selected_difficulty = "medium"
        self.opponent_info = {}
        self.available_sessions = []
        self.session_countdown = 0

        # Fonts
        self.font_lg = pygame.font.SysFont("monospace", max(28, cell_size + 6), bold=True)
        self.font_md = pygame.font.SysFont("monospace", max(20, cell_size), bold=True)
        self.font_sm = pygame.font.SysFont("monospace", max(14, cell_size - 6))

    def draw_mode_selection(self, screen: pygame.Surface):
        """Draw game mode selection screen"""
        screen.fill((20, 22, 30))

        title = self.font_lg.render("LINKED LIST SNAKE", True, (60, 210, 60))
        screen.blit(title, (self.W // 2 - title.get_width() // 2, self.H // 4))

        subtitle = self.font_md.render("Select Game Mode", True, (140, 150, 165))
        screen.blit(subtitle, (self.W // 2 - subtitle.get_width() // 2, self.H // 4 + 60))

        # Buttons
        modes = [
            ("SINGLE PLAYER", (60, 200, 60)),
            ("MULTIPLAYER HOST", (60, 100, 200)),
            ("MULTIPLAYER JOIN", (200, 100, 60))
        ]

        button_width = 200
        button_height = 60
        button_gap = 30
        start_y = self.H // 2

        for i, (text, color) in enumerate(modes):
            y = start_y + i * (button_height + button_gap)
            x = self.W // 2 - button_width // 2

            # Draw button
            pygame.draw.rect(screen, color, (x, y, button_width, button_height), border_radius=10)
            pygame.draw.rect(screen, (*color, 200), (x, y, button_width, button_height), 3, border_radius=10)

            # Text
            btn_text = self.font_md.render(text, True, (255, 255, 255))
            text_x = x + button_width // 2 - btn_text.get_width() // 2
            text_y = y + button_height // 2 - btn_text.get_height() // 2
            screen.blit(btn_text, (text_x, text_y))

        # Instructions
        help_text = self.font_sm.render("Click or press 1, 2, 3 to select", True, (100, 100, 100))
        screen.blit(help_text, (self.W // 2 - help_text.get_width() // 2, self.H - 50))

    def draw_multiplayer_lobby(self, screen: pygame.Surface, state: str):
        """Draw multiplayer lobby/waiting screen
        
        States:
        - waiting_for_player: Host waiting for join
        - joined: Guest joined, waiting for host to start
        - ready_check: Both players ready, countdown
        """
        screen.fill((20, 22, 30))

        if state == "waiting_for_player":
            title = self.font_lg.render("WAITING FOR PLAYER", True, (220, 180, 50))
            screen.blit(title, (self.W // 2 - title.get_width() // 2, self.H // 4))

            session_text = self.font_sm.render(f"Session ID: {self.session_id[:8]}...", True, (140, 150, 165))
            screen.blit(session_text, (self.W // 2 - session_text.get_width() // 2, self.H // 4 + 80))

            difficulty = self.font_md.render(f"Difficulty: {self.selected_difficulty.upper()}", True, (60, 210, 60))
            screen.blit(difficulty, (self.W // 2 - difficulty.get_width() // 2, self.H // 2 - 40))

            waiting = self.font_sm.render("Waiting...", True, (200, 200, 200))
            screen.blit(waiting, (self.W // 2 - waiting.get_width() // 2, self.H // 2 + 40))

        elif state == "joined":
            title = self.font_lg.render("PLAYER JOINED", True, (60, 210, 60))
            screen.blit(title, (self.W // 2 - title.get_width() // 2, self.H // 4))

            players_text = self.font_md.render(f"You: {self.nickname}", True, (140, 150, 165))
            screen.blit(players_text, (self.W // 2 - players_text.get_width() // 2, self.H // 2 - 40))

            opponent_text = self.font_md.render(f"Opponent: {self.opponent_info.get('nickname', 'Player 2')}", True, (200, 100, 50))
            screen.blit(opponent_text, (self.W // 2 - opponent_text.get_width() // 2, self.H // 2 + 20))

            wait_text = self.font_sm.render("Host will start the game...", True, (100, 100, 100))
            screen.blit(wait_text, (self.W // 2 - wait_text.get_width() // 2, self.H // 2 + 80))

        elif state == "ready_check":
            countdown_text = self.font_lg.render(f"STARTING IN {self.session_countdown}", True, (60, 210, 60))
            screen.blit(countdown_text, (self.W // 2 - countdown_text.get_width() // 2, self.H // 2 - 40))

            ready_text = self.font_md.render("GET READY!", True, (220, 60, 60))
            screen.blit(ready_text, (self.W // 2 - ready_text.get_width() // 2, self.H // 2 + 40))

    def draw_session_list(self, screen: pygame.Surface):
        """Draw available sessions list"""
        screen.fill((20, 22, 30))

        title = self.font_lg.render("AVAILABLE SESSIONS", True, (60, 210, 60))
        screen.blit(title, (self.W // 2 - title.get_width() // 2, self.H // 4))

        if not self.available_sessions:
            no_sessions = self.font_md.render("No sessions available", True, (140, 150, 165))
            screen.blit(no_sessions, (self.W // 2 - no_sessions.get_width() // 2, self.H // 2))

            refresh = self.font_sm.render("Press R to refresh or ESC to go back", True, (100, 100, 100))
            screen.blit(refresh, (self.W // 2 - refresh.get_width() // 2, self.H // 2 + 50))
        else:
            start_y = self.H // 3
            for i, session in enumerate(self.available_sessions[:5]):  # Show max 5
                y = start_y + i * 60
                host_text = f"Host: {session.get('host', 'Unknown')}"
                difficulty_text = f"Difficulty: {session.get('difficulty', 'medium').upper()}"

                host_render = self.font_sm.render(host_text, True, (140, 150, 165))
                diff_render = self.font_sm.render(difficulty_text, True, (60, 210, 60))

                screen.blit(host_render, (50, y))
                screen.blit(diff_render, (50, y + 20))

                # Highlight box
                pygame.draw.rect(screen, (60, 100, 200), (30, y - 5, self.W - 60, 50), 2)

            help_text = self.font_sm.render("Press 1-5 to join session or ESC to go back", True, (100, 100, 100))
            screen.blit(help_text, (self.W // 2 - help_text.get_width() // 2, self.H - 50))

    def draw_multiplayer_hud(self, screen: pygame.Surface, p1_score: int, p1_length: int, p1_name: str,
                            p2_score: int, p2_length: int, p2_name: str):
        """Draw two-player game HUD"""
        # Left side - Player 1
        p1_score_text = self.font_md.render(f"{p1_name}: {p1_score}", True, (60, 210, 60))
        p1_length_text = self.font_sm.render(f"Length: {p1_length}", True, (140, 150, 165))
        screen.blit(p1_score_text, (10, 10))
        screen.blit(p1_length_text, (10, 35))

        # Right side - Player 2
        p2_score_text = self.font_md.render(f"{p2_name}: {p2_score}", True, (150, 100, 200))
        p2_length_text = self.font_sm.render(f"Length: {p2_length}", True, (140, 150, 165))
        screen.blit(p2_score_text, (self.W - p2_score_text.get_width() - 10, 10))
        screen.blit(p2_length_text, (self.W - p2_length_text.get_width() - 10, 35))

        # Center divider
        pygame.draw.line(screen, (80, 80, 100), (self.W // 2, 0), (self.W // 2, 100), 2)

    def draw_multiplayer_gameover(self, screen: pygame.Surface, winner: str, winner_name: str,
                                   p1_score: int, p1_length: int, p1_name: str,
                                   p2_score: int, p2_length: int, p2_name: str):
        """Draw multiplayer game over screen with rematch option"""
        screen.fill((15, 15, 25))

        if winner == "p1":
            winner_text = f"{p1_name.upper()} WINS!"
            winner_color = (60, 210, 60)
        else:
            winner_text = f"{p2_name.upper()} WINS!"
            winner_color = (150, 100, 200)

        winner_render = self.font_lg.render(winner_text, True, winner_color)
        screen.blit(winner_render, (self.W // 2 - winner_render.get_width() // 2, self.H // 4))

        # Scores and lengths
        p1_info = self.font_md.render(f"{p1_name}: Score {p1_score} | Length {p1_length}", True, (60, 210, 60))
        p2_info = self.font_md.render(f"{p2_name}: Score {p2_score} | Length {p2_length}", True, (150, 100, 200))

        screen.blit(p1_info, (self.W // 2 - p1_info.get_width() // 2, self.H // 2 - 40))
        screen.blit(p2_info, (self.W // 2 - p2_info.get_width() // 2, self.H // 2 + 10))

        # Rematch buttons
        button_width = 200
        button_height = 50
        button_gap = 20

        rematch_y = self.H // 2 + 80
        rematch_x = self.W // 2 - button_width - button_gap // 2 - button_width // 2

        # Ready button
        pygame.draw.rect(screen, (60, 180, 60), (rematch_x - button_width - button_gap, rematch_y, button_width, button_height), border_radius=10)
        ready_text = self.font_md.render("READY", True, (255, 255, 255))
        screen.blit(ready_text, (rematch_x - button_width - button_gap + button_width // 2 - ready_text.get_width() // 2,
                                 rematch_y + button_height // 2 - ready_text.get_height() // 2))

        # Cancel button
        pygame.draw.rect(screen, (180, 60, 60), (rematch_x + button_gap, rematch_y, button_width, button_height), border_radius=10)
        cancel_text = self.font_md.render("CANCEL", True, (255, 255, 255))
        screen.blit(cancel_text, (rematch_x + button_gap + button_width // 2 - cancel_text.get_width() // 2,
                                  rematch_y + button_height // 2 - cancel_text.get_height() // 2))

        help_text = self.font_sm.render("Press R or C to choose", True, (100, 100, 100))
        screen.blit(help_text, (self.W // 2 - help_text.get_width() // 2, self.H - 50))


async def multiplayer_mode(client: MultiplayerClient, is_host: bool, nickname: str, 
                           difficulty: str, W: int, H: int, CELL: int) -> Optional[str]:
    """
    Run multiplayer game mode
    Returns: "menu" to return to menu, None to exit
    """
    pygame.init()
    screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption("Linked List Snake - Multiplayer")
    clock = pygame.time.Clock()

    manager = MultiplayerManager(W, H, CELL)
    manager.nickname = nickname
    manager.selected_difficulty = difficulty

    # Placeholder for now - actual 2-player game logic would go here
    state = "lobby"

    while True:
        dt = min(clock.tick(60) / 1000.0, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if client:
                        client.disconnect()
                    return "menu"

        screen.fill((20, 22, 30))

        # Draw placeholder
        text = manager.font_lg.render("MULTIPLAYER MODE", True, (60, 210, 60))
        screen.blit(text, (W // 2 - text.get_width() // 2, H // 2 - 50))

        help_text = manager.font_sm.render("Multiplayer game in progress (placeholder)", True, (100, 100, 100))
        screen.blit(help_text, (W // 2 - help_text.get_width() // 2, H // 2 + 50))

        pygame.display.flip()
        await asyncio.sleep(0)
