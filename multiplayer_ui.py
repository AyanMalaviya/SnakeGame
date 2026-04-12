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

    # Import required modules and functions
    from main import (make_head, make_body, make_tail, make_stone, make_apple,
                      SnakeLinkedList, DIFFICULTIES, DIR_ANGLE, interpolate, 
                      draw_button, asset_path)
    from multiplayer_logic import MultiplayerGameLogic
    import os
    
    # Fonts
    font_names = ["monospace", "dejavu sans mono", "courier new", "consolas"]
    for font_name in font_names:
        try:
            font_lg = pygame.font.SysFont(font_name, max(28, CELL + 6), bold=True)
            font_md = pygame.font.SysFont(font_name, max(20, CELL), bold=True)
            font_sm = pygame.font.SysFont(font_name, max(14, CELL - 6))
            break
        except:
            continue
    else:
        font_lg = pygame.font.Font(None, max(28, CELL + 6))
        font_md = pygame.font.Font(None, max(20, CELL))
        font_sm = pygame.font.Font(None, max(14, CELL - 6))
    
    COLS = W // CELL
    ROWS = H // CELL
    
    # Create sprites
    img_head  = make_head(CELL)
    img_body  = make_body(CELL)
    img_tail  = make_tail(CELL)
    img_stone = make_stone(CELL)
    img_apple = pygame.image.load(asset_path("apple.png")).convert_alpha()
    
    heads = {d: pygame.transform.rotate(img_head, a) for d, a in DIR_ANGLE.items()}
    tails = {d: pygame.transform.rotate(img_tail, a) for d, a in DIR_ANGLE.items()}
    
    # Grid surface
    grid_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    for gx in range(COLS):
        for gy in range(ROWS):
            pygame.draw.circle(grid_surf, (52, 56, 65),
                               (gx * CELL + CELL // 2, gy * CELL + CELL // 2), 1)
    
    # Game state and player setup
    cfg = DIFFICULTIES[difficulty]
    SPEED = cfg["speed"]
    
    # Create two snakes - P1 on left, P2 on right
    snake_p1 = SnakeLinkedList(COLS // 3, ROWS // 2)
    snake_p2 = SnakeLinkedList(2 * COLS // 3, ROWS // 2)
    
    p1_dx = p1_dy = 0
    p1_ndx, p1_ndy = 1, 0
    p1_progress = 0.0
    p1_score = 0
    p1_tail_dir = (1, 0)
    
    p2_dx = p2_dy = 0
    p2_ndx, p2_ndy = -1, 0
    p2_progress = 0.0
    p2_score = 0
    p2_tail_dir = (-1, 0)
    
    # Apple and stones
    apple_x = random.randint(0, COLS - 1)
    apple_y = random.randint(0, ROWS - 1)
    
    stones = set()
    while len(stones) < cfg["stones"]:
        sx, sy = random.randint(0, COLS - 1), random.randint(0, ROWS - 1)
        if (sx, sy) not in {(COLS // 3, ROWS // 2), (2 * COLS // 3, ROWS // 2), (apple_x, apple_y)}:
            stones.add((sx, sy))
    
    state = "countdown"
    countdown = 3.0
    game_over_info = None
    
    while True:
        dt = min(clock.tick(60) / 1000.0, 0.05)
        
        # ==================== EVENTS ====================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if client:
                        client.disconnect()
                    return "menu"
                    
                if state == "playing":
                    # P1 controls: Arrow keys
                    if event.key == pygame.K_UP and p1_dy != 1:
                        p1_ndx, p1_ndy = 0, -1
                    elif event.key == pygame.K_DOWN and p1_dy != -1:
                        p1_ndx, p1_ndy = 0, 1
                    elif event.key == pygame.K_LEFT and p1_dx != 1:
                        p1_ndx, p1_ndy = -1, 0
                    elif event.key == pygame.K_RIGHT and p1_dx != -1:
                        p1_ndx, p1_ndy = 1, 0
                        
                    # P2 controls: WASD
                    if event.key == pygame.K_w and p2_dy != 1:
                        p2_ndx, p2_ndy = 0, -1
                    elif event.key == pygame.K_s and p2_dy != -1:
                        p2_ndx, p2_ndy = 0, 1
                    elif event.key == pygame.K_a and p2_dx != 1:
                        p2_ndx, p2_ndy = -1, 0
                    elif event.key == pygame.K_d and p2_dx != -1:
                        p2_ndx, p2_ndy = 1, 0
                        
            if event.type == pygame.MOUSEBUTTONDOWN and state == "game_over":
                mx, my = event.pos
                # Rematch button
                if W//2 - 100 <= mx <= W//2 + 100 and H//2 + 80 <= my <= H//2 + 132:
                    return "menu"
        
        # ==================== COUNTDOWN ====================
        if state == "countdown":
            countdown -= dt
            if countdown <= 0:
                state = "playing"
        
        # ==================== GAME LOGIC ====================
        elif state == "playing":
            p1_progress += dt * SPEED
            p2_progress += dt * SPEED
            
            ate_apple_p1 = False
            ate_apple_p2 = False
            
            # P1 move
            if p1_progress >= 1.0:
                p1_progress -= 1.0
                p1_dx, p1_dy = p1_ndx, p1_ndy
                
                new_x = (snake_p1.head.x + p1_dx) % COLS
                new_y = (snake_p1.head.y + p1_dy) % ROWS
                
                if new_x == apple_x and new_y == apple_y:
                    ate_apple_p1 = True
                    p1_score += 10 * cfg["score_mult"]
                
                snake_p1.move(new_x, new_y, ate_apple_p1)
            
            # P2 move
            if p2_progress >= 1.0:
                p2_progress -= 1.0
                p2_dx, p2_dy = p2_ndx, p2_ndy
                
                new_x = (snake_p2.head.x + p2_dx) % COLS
                new_y = (snake_p2.head.y + p2_dy) % ROWS
                
                if new_x == apple_x and new_y == apple_y:
                    ate_apple_p2 = True
                    p2_score += 10 * cfg["score_mult"]
                
                snake_p2.move(new_x, new_y, ate_apple_p2)
            
            # Both ate apple - spawn new one
            if ate_apple_p1 or ate_apple_p2:
                while True:
                    apple_x = random.randint(0, COLS - 1)
                    apple_y = random.randint(0, ROWS - 1)
                    if (apple_x, apple_y) not in stones:
                        break
            
            # Check collisions every frame
            p1_positions = snake_p1.get_positions()
            p2_positions = snake_p2.get_positions()
            
            # Check two-player collisions (head-to-head, head-to-body)
            p1_dies_mp, p2_dies_mp, collision_type = MultiplayerGameLogic.evaluate_multiplayer_collision(
                p1_positions[0], p1_positions,
                (p1_dx, p1_dy),
                p2_positions[0], p2_positions,
                (p2_dx, p2_dy),
                COLS, ROWS
            )
            
            # Check self-collisions
            p1_self_died = MultiplayerGameLogic.check_self_collision(p1_positions)
            p2_self_died = MultiplayerGameLogic.check_self_collision(p2_positions)
            
            # Check stone collisions
            p1_stone_died = MultiplayerGameLogic.check_stone_collision(p1_positions[0], stones)
            p2_stone_died = MultiplayerGameLogic.check_stone_collision(p2_positions[0], stones)
            
            # Combine all death conditions
            p1_dies = p1_dies_mp or p1_self_died or p1_stone_died
            p2_dies = p2_dies_mp or p2_self_died or p2_stone_died
            
            if p1_dies or p2_dies:
                if p1_dies and p2_dies:
                    winner = "TIE"
                elif p1_dies:
                    winner = "P2"
                else:
                    winner = "P1"
                    
                game_over_info = {
                    "winner": winner,
                    "p1_score": p1_score,
                    "p2_score": p2_score,
                    "p1_length": snake_p1.length,
                    "p2_length": snake_p2.length
                }
                state = "game_over"
        
        # ==================== RENDER ====================
        screen.fill((40, 44, 52))
        screen.blit(grid_surf, (0, 0))
        
        # Stones
        for sx, sy in stones:
            screen.blit(img_stone, (sx * CELL, sy * CELL))
        
        # Apple
        pulse = 0.05 * math.sin(pygame.time.get_ticks() * 0.005)
        apple_size = int(CELL * (1.0 + pulse))
        apple_scaled = pygame.transform.smoothscale(img_apple, (apple_size, apple_size))
        off = (CELL - apple_size) // 2
        screen.blit(apple_scaled, (apple_x * CELL + off, apple_y * CELL + off))
        
        # Render snakes
        def render_snake(snake, dx, dy, progress, is_p1=True):
            positions = snake.get_positions()
            
            if not is_p1:
                # Red snake for P2
                red_head = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
                pygame.draw.rect(red_head, (210, 60, 60), (0, 0, CELL, CELL), border_radius=12)
                pygame.draw.rect(red_head, (160, 30, 30), (CELL // 2, 3, CELL // 2, CELL - 6), border_radius=8)
                pygame.draw.circle(red_head, (240, 240, 240), (CELL - 7, 8), 5)
                pygame.draw.circle(red_head, (240, 240, 240), (CELL - 7, CELL - 8), 5)
                pygame.draw.circle(red_head, (10, 10, 10), (CELL - 5, 8), 2)
                pygame.draw.circle(red_head, (10, 10, 10), (CELL - 5, CELL - 8), 2)
                
                red_heads = {d: pygame.transform.rotate(red_head, a) for d, a in DIR_ANGLE.items()}
                
                red_body = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
                pygame.draw.rect(red_body, (200, 50, 50), (1, 1, CELL - 2, CELL - 2), border_radius=6)
                pygame.draw.rect(red_body, (150, 30, 30), (5, 5, CELL - 10, CELL - 10), border_radius=4)
                
                img_body_use = red_body
                heads_use = red_heads
            else:
                img_body_use = img_body
                heads_use = heads
            
            nx_head = (positions[0][0] + (1 if dx == 1 else -1 if dx == -1 else 0)) % COLS
            ny_head = (positions[0][1] + (1 if dy == 1 else -1 if dy == -1 else 0)) % ROWS
            next_positions = [(nx_head, ny_head)] + positions[:-1]
            
            for i, ((cx, cy), (nxt_x, nxt_y)) in enumerate(zip(positions, next_positions)):
                rx, ry = interpolate(cx, cy, nxt_x, nxt_y, progress, COLS, ROWS, CELL)
                if i == 0:
                    screen.blit(heads_use.get((dx, dy), img_head), (rx, ry))
                elif i == len(positions) - 1:
                    screen.blit(tails.get((dx, dy), img_tail), (rx, ry))
                else:
                    screen.blit(img_body_use, (rx, ry))
        
        render_snake(snake_p1, p1_dx, p1_dy, p1_progress, is_p1=True)
        render_snake(snake_p2, p2_dx, p2_dy, p2_progress, is_p1=False)
        
        # HUD
        hud_p1 = font_sm.render(f"P1 ({nickname}): {p1_score} pts | Len: {snake_p1.length}", 
                                True, (80, 200, 80))
        screen.blit(hud_p1, (10, 10))
        
        hud_p2 = font_sm.render(f"P2 (Opponent): {p2_score} pts | Len: {snake_p2.length}", 
                                True, (200, 80, 80))
        screen.blit(hud_p2, (W - hud_p2.get_width() - 10, 10))
        
        # Countdown display
        if state == "countdown":
            cd_val = max(0, int(countdown) + 1)
            if cd_val > 0:
                cd_txt = font_lg.render(str(cd_val), True, (200, 200, 100))
            else:
                cd_txt = font_lg.render("GO!", True, (100, 200, 100))
            screen.blit(cd_txt, (W // 2 - cd_txt.get_width() // 2, H // 2 - cd_txt.get_height() // 2))
        
        # Game over screen
        if state == "game_over" and game_over_info:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            if game_over_info["winner"] == "TIE":
                go_txt = font_lg.render("TIE!", True, (200, 200, 100))
            elif game_over_info["winner"] == "P1":
                go_txt = font_lg.render("YOU WIN!", True, (100, 200, 100))
            else:
                go_txt = font_lg.render("OPPONENT WINS!", True, (200, 100, 100))
            
            screen.blit(go_txt, (W // 2 - go_txt.get_width() // 2, H // 2 - 80))
            
            score_txt = font_md.render(
                f"P1: {game_over_info['p1_score']} pts (len {game_over_info['p1_length']})  |  " +
                f"P2: {game_over_info['p2_score']} pts (len {game_over_info['p2_length']})",
                True, (200, 200, 200)
            )
            screen.blit(score_txt, (W // 2 - score_txt.get_width() // 2, H // 2 - 20))
            
            # Rematch button
            draw_button(screen, W // 2 - 100, H // 2 + 80, 200, 52, (100, 150, 200), alpha=200)
            rematch_txt = font_md.render("BACK TO MENU", True, (255, 255, 255))
            screen.blit(rematch_txt, (W // 2 - rematch_txt.get_width() // 2,
                                      H // 2 + 80 + 26 - rematch_txt.get_height() // 2))
        
        pygame.display.flip()
        await asyncio.sleep(0)
