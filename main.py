# -*- coding: utf-8 -*-
import pygame
import random
import sys
import math
import asyncio
import os

# ==========================================
# DOUBLY LINKED LIST DATA STRUCTURE
# ==========================================
class Node:
    def __init__(self, x, y):
        self.x = x        # Grid X position
        self.y = y        # Grid Y position
        self.next = None  # Points toward the tail
        self.prev = None  # Points toward the head

class SnakeLinkedList:
    def __init__(self, x, y):
        self.head = Node(x, y)
        self.tail = self.head
        self.length = 1

    def move(self, new_x, new_y, ate_apple=False):
        # Create a new head node at the new grid cell
        new_head = Node(new_x, new_y)
        new_head.next = self.head
        self.head.prev = new_head
        self.head = new_head
        if not ate_apple:
            # Sever the tail node -- Python GC cleans it up
            self.tail = self.tail.prev
            self.tail.next = None
        else:
            self.length += 1

    def check_body_collision(self):
        # Traverse the list from neck to tail checking if head overlaps
        curr = self.head.next
        while curr:
            if curr.x == self.head.x and curr.y == self.head.y:
                return True
            curr = curr.next
        return False

    def get_positions(self):
        # Returns all (x, y) grid positions as a list from head to tail
        positions = []
        curr = self.head
        while curr:
            positions.append((curr.x, curr.y))
            curr = curr.next
        return positions


# ==========================================
# SPRITE GENERATORS
# ==========================================
def make_head(cell):
    s = pygame.Surface((cell, cell), pygame.SRCALPHA)
    pygame.draw.rect(s, (60, 210, 60), (0, 0, cell, cell), border_radius=12)
    pygame.draw.rect(s, (30, 160, 30), (cell // 2, 3, cell // 2, cell - 6), border_radius=8)
    pygame.draw.circle(s, (240, 240, 240), (cell - 7, 8), 5)
    pygame.draw.circle(s, (240, 240, 240), (cell - 7, cell - 8), 5)
    pygame.draw.circle(s, (10, 10, 10), (cell - 5, 8), 2)
    pygame.draw.circle(s, (10, 10, 10), (cell - 5, cell - 8), 2)
    pygame.draw.line(s, (220, 30, 30), (cell - 1, cell // 2), (cell + 5, cell // 2 - 4), 2)
    pygame.draw.line(s, (220, 30, 30), (cell - 1, cell // 2), (cell + 5, cell // 2 + 4), 2)
    return s

def make_body(cell):
    s = pygame.Surface((cell, cell), pygame.SRCALPHA)
    pygame.draw.rect(s, (50, 185, 50), (1, 1, cell - 2, cell - 2), border_radius=6)
    pygame.draw.rect(s, (30, 140, 30), (5, 5, cell - 10, cell - 10), border_radius=4)
    pygame.draw.ellipse(s, (70, 210, 70), (4, 5, 12, 7))
    pygame.draw.ellipse(s, (70, 210, 70), (4, cell - 12, 12, 7))
    return s

def make_tail(cell):
    s = pygame.Surface((cell, cell), pygame.SRCALPHA)
    pts = [(0, 5), (cell - 8, 3), (cell, cell // 2), (cell - 8, cell - 3), (0, cell - 5)]
    pygame.draw.polygon(s, (60, 210, 60), pts)
    inner = [(3, 8), (cell - 10, 6), (cell - 5, cell // 2), (cell - 10, cell - 6), (3, cell - 8)]
    pygame.draw.polygon(s, (30, 160, 30), inner)
    return s

def make_stone(cell):
    s = pygame.Surface((cell, cell), pygame.SRCALPHA)
    oct_pts = [(5, 0), (cell-5, 0), (cell, 5), (cell, cell-5),
               (cell-5, cell), (5, cell), (0, cell-5), (0, 5)]
    pygame.draw.polygon(s, (110, 110, 115), oct_pts)
    pygame.draw.polygon(s, (160, 160, 165), [(6, 2), (cell-6, 2), (cell-4, 9), (6, 9)])
    pygame.draw.polygon(s, (70, 70, 75), [(6, cell-9), (cell-6, cell-9), (cell-4, cell-2), (6, cell-2)])
    pygame.draw.line(s, (80, 80, 85), (cell//3, 6), (cell//2, cell-6), 1)
    return s

def make_apple(cell):
    s = pygame.Surface((cell, cell), pygame.SRCALPHA)
    pygame.draw.circle(s, (210, 30, 30), (cell // 2, cell // 2 + 3), cell // 2 - 3)
    pygame.draw.circle(s, (255, 110, 110), (cell // 2 - 5, cell // 2 - 4), 5)
    pygame.draw.circle(s, (255, 180, 180), (cell // 2 - 6, cell // 2 - 5), 2)
    pygame.draw.rect(s, (100, 60, 20), (cell // 2 - 1, 0, 3, 7))
    pygame.draw.ellipse(s, (40, 190, 40), (cell // 2 + 1, 1, 10, 6))
    return s


# ==========================================
# SMOOTH INTERPOLATION
# ==========================================
def interpolate(cx, cy, nx, ny, t, gw, gh, cell):
    ddx = nx - cx
    ddy = ny - cy
    # Skip lerp on portal wrap (modulus jump > half the grid)
    if abs(ddx) > gw // 2: ddx = 0
    if abs(ddy) > gh // 2: ddy = 0
    # Ease-in-out curve for organic movement
    t_smooth = t * t * (3 - 2 * t)
    return int((cx + ddx * t_smooth) * cell), int((cy + ddy * t_smooth) * cell)


DIR_ANGLE = {(1, 0): 0, (-1, 0): 180, (0, -1): 90, (0, 1): -90}


def asset_path(name):
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, name)
    return os.path.join(os.path.dirname(__file__), name)

# ==========================================
# DIFFICULTY SETTINGS
# ==========================================
DIFFICULTIES = {
    "easy":   {"speed": 7,  "stones": 4,  "score_mult": 1, "color": (80, 200, 80),  "label": "EASY"},
    "medium": {"speed": 8, "stones": 12, "score_mult": 2, "color": (220, 180, 50), "label": "MEDIUM"},
    "hard":   {"speed": 9, "stones": 22, "score_mult": 3, "color": (220, 60, 60),  "label": "HARD"},
}
DIFF_KEYS = ["easy", "medium", "hard"]


# ==========================================
# D-PAD HELPERS
# ==========================================
def get_dpad_rects(cx, cy, btn_r):
    return {
        "up":    (cx,             cy - btn_r * 2),
        "down":  (cx,             cy + btn_r * 2),
        "left":  (cx - btn_r * 2, cy),
        "right": (cx + btn_r * 2, cy),
    }

def draw_dpad(screen, dpad_pos, btn_r):
    for direction, (bx, by) in dpad_pos.items():
        btn_surf = pygame.Surface((btn_r * 2, btn_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(btn_surf, (255, 255, 255, 45), (btn_r, btn_r), btn_r)
        pygame.draw.circle(btn_surf, (255, 255, 255, 110), (btn_r, btn_r), btn_r, 2)
        screen.blit(btn_surf, (bx - btn_r, by - btn_r))
        ar = btn_r // 2
        if   direction == "up":    pts = [(bx, by-ar), (bx-ar, by+ar//2), (bx+ar, by+ar//2)]
        elif direction == "down":  pts = [(bx, by+ar), (bx-ar, by-ar//2), (bx+ar, by-ar//2)]
        elif direction == "left":  pts = [(bx-ar, by), (bx+ar//2, by-ar), (bx+ar//2, by+ar)]
        else:                      pts = [(bx+ar, by), (bx-ar//2, by-ar), (bx-ar//2, by+ar)]
        pygame.draw.polygon(screen, (180, 195, 210), pts)

def hit_dpad(mx, my, dpad_pos, btn_r):
    for direction, (bx, by) in dpad_pos.items():
        if math.hypot(mx - bx, my - by) <= btn_r:
            return direction
    return None


# ==========================================
# BUTTON DRAW HELPER
# ==========================================
def draw_button(screen, x, y, w, h, color, alpha=180, radius=14):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, (*color, alpha), (0, 0, w, h), border_radius=radius)
    screen.blit(surf, (x, y))


def draw_pause_icon_button(screen, rect, is_paused):
    surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    base = (70, 160, 90, 205) if is_paused else (70, 140, 210, 205)
    pygame.draw.ellipse(surf, base, (0, 0, rect.w, rect.h))
    pygame.draw.ellipse(surf, (255, 255, 255, 130), (0, 0, rect.w, rect.h), 2)

    if is_paused:
        tri = [
            (rect.w // 2 - rect.w // 8, rect.h // 2 - rect.h // 5),
            (rect.w // 2 - rect.w // 8, rect.h // 2 + rect.h // 5),
            (rect.w // 2 + rect.w // 5, rect.h // 2),
        ]
        pygame.draw.polygon(surf, (245, 245, 245), tri)
    else:
        bar_w = max(4, rect.w // 8)
        bar_h = max(16, rect.h // 3)
        bar_y = rect.h // 2 - bar_h // 2
        gap = max(4, bar_w)
        cx = rect.w // 2
        pygame.draw.rect(surf, (245, 245, 245),
                         (cx - gap - bar_w, bar_y, bar_w, bar_h), border_radius=2)
        pygame.draw.rect(surf, (245, 245, 245),
                         (cx + gap, bar_y, bar_w, bar_h), border_radius=2)

    screen.blit(surf, rect.topleft)


# ==========================================
# MAIN GAME
# ==========================================
async def main():
    pygame.init()

    # Fullscreen: read real monitor dimensions
    info = pygame.display.Info()
    W    = info.current_w
    H    = info.current_h
    screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption("Linked List Snake")
    clock = pygame.time.Clock()
    FPS   = 60

    # Dynamic cell size -- scales to any screen resolution
    CELL = max(min(W // 28, H // 22), 18)
    COLS = W // CELL
    ROWS = H // CELL

    # Fonts scaled to cell size
    font_lg = pygame.font.SysFont("consolas", max(28, CELL + 6), bold=True)
    font_md = pygame.font.SysFont("consolas", max(20, CELL),     bold=True)
    font_sm = pygame.font.SysFont("consolas", max(14, CELL - 6))

    # Build all sprites once at startup
    img_head  = make_head(CELL)
    img_body  = make_body(CELL)
    img_tail  = make_tail(CELL)
    img_stone = make_stone(CELL)
    img_apple = pygame.image.load(asset_path("apple.png")).convert_alpha()

    # Pre-rotate head and tail for all 4 directions -- avoids per-frame cost
    heads = {d: pygame.transform.rotate(img_head, a) for d, a in DIR_ANGLE.items()}
    tails = {d: pygame.transform.rotate(img_tail, a) for d, a in DIR_ANGLE.items()}

    # Grid dot surface -- rendered once, blit cheaply every frame
    grid_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    for gx in range(COLS):
        for gy in range(ROWS):
            pygame.draw.circle(grid_surf, (52, 56, 65),
                               (gx * CELL + CELL // 2, gy * CELL + CELL // 2), 1)

    # D-pad position: bottom-right corner, scales with screen
    DPAD_CX  = W - max(130, W // 6)
    DPAD_CY  = H - max(130, H // 6)
    BTN_R    = max(28, CELL + 6)
    dpad_pos = get_dpad_rects(DPAD_CX, DPAD_CY, BTN_R)

    # ---- GAME STATE ----
    state         = "menu"
    selected_diff = "medium"
    snake         = SnakeLinkedList(COLS // 2, ROWS // 2)
    dx = dy = ndx = ndy = 0
    progress      = 0.0
    score         = 0
    tail_dir      = (1, 0)
    apple_x = apple_y = 0
    stones        = set()
    SPEED         = 10.0
    bonus_points_total = 0
    bonus_moves_left = 0
    move_count    = 0
    last_apple_move = None
    swipe_start   = None
    SWIPE_MIN     = CELL * 1.5
    is_paused     = False

    # Top-right icon button + pause overlay actions
    UI_BTN_SIZE = max(44, CELL * 2)
    UI_BTN_PAD = 10
    pause_btn_rect = pygame.Rect(W - UI_BTN_SIZE - UI_BTN_PAD, UI_BTN_PAD, UI_BTN_SIZE, UI_BTN_SIZE)
    PAUSE_BTN_W = max(190, W // 5)
    PAUSE_BTN_H = 52
    PAUSE_BTN_GAP = 12
    resume_btn_rect = pygame.Rect(W // 2 - PAUSE_BTN_W // 2, H // 2 + 26,
                                  PAUSE_BTN_W, PAUSE_BTN_H)
    pause_menu_btn_rect = pygame.Rect(W // 2 - PAUSE_BTN_W // 2,
                                      H // 2 + 26 + PAUSE_BTN_H + PAUSE_BTN_GAP,
                                      PAUSE_BTN_W, PAUSE_BTN_H)

    def init_game(diff):
        nonlocal snake, dx, dy, ndx, ndy, progress, score
        nonlocal tail_dir, apple_x, apple_y, stones, SPEED, is_paused
        nonlocal bonus_points_total, bonus_moves_left
        nonlocal move_count, last_apple_move

        cfg   = DIFFICULTIES[diff]
        SPEED = cfg["speed"]
        score = 0
        bonus_points_total = 0
        bonus_moves_left = 0
        move_count = 0
        last_apple_move = None
        is_paused = False
        progress  = 0.0
        dx = dy   = 0
        ndx, ndy  = 1, 0
        tail_dir  = (1, 0)

        snake   = SnakeLinkedList(COLS // 2, ROWS // 2)
        apple_x = random.randint(0, COLS - 1)
        apple_y = random.randint(0, ROWS - 1)

        stones = set()
        while len(stones) < cfg["stones"]:
            sx, sy = random.randint(0, COLS-1), random.randint(0, ROWS-1)
            if (sx, sy) not in {(COLS//2, ROWS//2), (apple_x, apple_y)}:
                stones.add((sx, sy))

    # ---- MAIN LOOP ----
    while True:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        # ==========================================
        # EVENTS
        # ==========================================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # ---------- MENU ----------
            if state == "menu":
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        idx = DIFF_KEYS.index(selected_diff)
                        selected_diff = DIFF_KEYS[(idx - 1) % 3]
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        idx = DIFF_KEYS.index(selected_diff)
                        selected_diff = DIFF_KEYS[(idx + 1) % 3]
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        init_game(selected_diff)
                        state = "game"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    for i, dk in enumerate(DIFF_KEYS):
                        bx = W//2 + (i - 1) * (W//4)
                        by, bw, bh = H//2 + 30, W//5, 60
                        if bx - bw//2 <= mx <= bx + bw//2 and by <= my <= by + bh:
                            selected_diff = dk
                    # Play button hit area
                    if abs(mx - W//2) < 80 and H//2 + 104 <= my <= H//2 + 156:
                        init_game(selected_diff)
                        state = "game"

            # ---------- GAME ----------
            elif state == "game":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        is_paused = not is_paused
                    elif event.key == pygame.K_ESCAPE:
                        is_paused = False
                        state = "menu"
                    # Arrow Keys + WASD both supported
                    elif not is_paused:
                        if   event.key in (pygame.K_UP,    pygame.K_w) and dy != 1:  ndx, ndy = 0, -1
                        elif event.key in (pygame.K_DOWN,  pygame.K_s) and dy != -1: ndx, ndy = 0,  1
                        elif event.key in (pygame.K_LEFT,  pygame.K_a) and dx != 1:  ndx, ndy = -1, 0
                        elif event.key in (pygame.K_RIGHT, pygame.K_d) and dx != -1: ndx, ndy =  1, 0

                # D-pad tap OR start swipe
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos

                    if pause_btn_rect.collidepoint(mx, my):
                        is_paused = not is_paused
                        swipe_start = None
                        continue

                    if is_paused:
                        if resume_btn_rect.collidepoint(mx, my):
                            is_paused = False
                        elif pause_menu_btn_rect.collidepoint(mx, my):
                            is_paused = False
                            state = "menu"
                        swipe_start = None
                        continue

                    hit = hit_dpad(mx, my, dpad_pos, BTN_R)
                    if   hit == "up"    and dy != 1:  ndx, ndy = 0, -1
                    elif hit == "down"  and dy != -1: ndx, ndy = 0,  1
                    elif hit == "left"  and dx != 1:  ndx, ndy = -1, 0
                    elif hit == "right" and dx != -1: ndx, ndy =  1, 0
                    else:
                        swipe_start = (mx, my)

                # Evaluate swipe on release
                if event.type == pygame.MOUSEBUTTONUP and (not is_paused) and swipe_start:
                    ex, ey = event.pos
                    sdx    = ex - swipe_start[0]
                    sdy    = ey - swipe_start[1]
                    if math.hypot(sdx, sdy) > SWIPE_MIN:
                        if abs(sdx) > abs(sdy):
                            if sdx > 0 and dx != -1: ndx, ndy =  1, 0
                            elif sdx < 0 and dx != 1: ndx, ndy = -1, 0
                        else:
                            if sdy > 0 and dy != -1: ndx, ndy = 0,  1
                            elif sdy < 0 and dy != 1: ndx, ndy = 0, -1
                    swipe_start = None

            # ---------- GAME OVER ----------
            elif state == "gameover":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        init_game(selected_diff); state = "game"
                    elif event.key in (pygame.K_m, pygame.K_ESCAPE):
                        state = "menu"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if abs(mx - W//2) < 100 and H//2 + 50 <= my <= H//2 + 102:
                        init_game(selected_diff); state = "game"
                    if abs(mx - W//2) < 100 and H//2 + 112 <= my <= H//2 + 164:
                        state = "menu"

        # ==========================================
        # RENDER: MENU
        # ==========================================
        if state == "menu":
            screen.fill((20, 22, 30))

            title = font_lg.render("LINKED LIST SNAKE", True, (60, 210, 60))
            screen.blit(title, (W//2 - title.get_width()//2, H//4))

            sub = font_sm.render("Select Difficulty", True, (140, 150, 165))
            screen.blit(sub, (W//2 - sub.get_width()//2, H//4 + 52))

            for i, dk in enumerate(DIFF_KEYS):
                cfg  = DIFFICULTIES[dk]
                bx   = W//2 + (i - 1) * (W//4)
                by   = H//2 + 30
                bw, bh = W//5, 60
                is_sel = (dk == selected_diff)

                draw_button(screen, bx - bw//2, by, bw, bh,
                            cfg["color"], alpha=210 if is_sel else 60, radius=14)
                if is_sel:
                    pygame.draw.rect(screen, cfg["color"],
                                     (bx - bw//2, by, bw, bh), 3, border_radius=14)

                lbl = font_md.render(cfg["label"], True,
                                     (255,255,255) if is_sel else (160,160,160))
                screen.blit(lbl, (bx - lbl.get_width()//2, by + bh//2 - lbl.get_height()//2))

                hint = font_sm.render("x" + str(cfg["score_mult"]) + " score", True,
                                      (210,210,210) if is_sel else (100,100,100))
                screen.blit(hint, (bx - hint.get_width()//2, by + bh + 6))

            # Play button
            draw_button(screen, W//2 - 80, H//2 + 104, 160, 52, (60, 200, 60), alpha=210)
            play_txt = font_md.render(">> PLAY", True, (255, 255, 255))
            screen.blit(play_txt, (W//2 - play_txt.get_width()//2,
                                   H//2 + 104 + 26 - play_txt.get_height()//2))

            # Controls hints -- all plain ASCII
            hints = [
                "Left / Right or A / D  :  Switch Difficulty",
                "Arrow Keys / WASD      :  Move Snake",
                "Swipe or D-Pad         :  Mobile Controls",
                "P                      :  Pause / Resume",
                "ESC                    :  Back to Menu",
            ]
            for j, h in enumerate(hints):
                ht = font_sm.render(h, True, (80, 95, 115))
                screen.blit(ht, (W//2 - ht.get_width()//2, H * 3//4 + j * 28))

        # ==========================================
        # RENDER: GAME
        # ==========================================
        elif state == "game":
            # Advance interpolation at game speed (independent of FPS)
            if not is_paused:
                progress += dt * SPEED

            # Predict next head position for smooth rendering before logic fires
            nx_head = (snake.head.x + ndx) % COLS
            ny_head = (snake.head.y + ndy) % ROWS

            # Logic tick: fires once per grid cell
            if (not is_paused) and progress >= 1.0:
                progress -= 1.0
                dx, dy = ndx, ndy

                new_x = (snake.head.x + dx) % COLS
                new_y = (snake.head.y + dy) % ROWS
                move_count += 1

                # Rule 1: Stone collision
                if (new_x, new_y) in stones:
                    state = "gameover"

                # Rule 2: Apple
                ate_apple = (new_x == apple_x and new_y == apple_y)
                if ate_apple:
                    score += 10 * DIFFICULTIES[selected_diff]["score_mult"]
                    # Combo bonus: second apple eaten within 2 moves grants +1.
                    if last_apple_move is not None and (move_count - last_apple_move) < 3:
                        score += 1
                        bonus_points_total += 1
                    last_apple_move = move_count
                    while True:
                        apple_x = random.randint(0, COLS - 1)
                        apple_y = random.randint(0, ROWS - 1)
                        if (apple_x, apple_y) not in stones:
                            break

                if last_apple_move is None:
                    bonus_moves_left = 0
                else:
                    bonus_moves_left = max(0, 2 - (move_count - last_apple_move))

                # Move the doubly linked list one cell
                snake.move(new_x, new_y, ate_apple)

                # Rule 3: Self-collision
                if snake.check_body_collision():
                    state = "gameover"

                nx_head = (snake.head.x + dx) % COLS
                ny_head = (snake.head.y + dy) % ROWS

            # Background
            screen.fill((40, 44, 52))
            screen.blit(grid_surf, (0, 0))

            # Stones
            for sx, sy in stones:
                screen.blit(img_stone, (sx * CELL, sy * CELL))

            # Apple with breathing pulse
            pulse        = 0.05 * math.sin(pygame.time.get_ticks() * 0.005)
            apple_size   = int(CELL * (1.0 + pulse))
            apple_scaled = pygame.transform.smoothscale(img_apple, (apple_size, apple_size))
            off = (CELL - apple_size) // 2
            screen.blit(apple_scaled, (apple_x * CELL + off, apple_y * CELL + off))

            # Snake -- traverse linked list, interpolate each segment smoothly
            positions      = snake.get_positions()
            next_positions = [(nx_head, ny_head)] + positions[:-1]

            for i, ((cx, cy), (nxt_x, nxt_y)) in enumerate(zip(positions, next_positions)):
                rx, ry = interpolate(cx, cy, nxt_x, nxt_y, progress, COLS, ROWS, CELL)
                if i == 0:
                    screen.blit(heads.get((dx, dy), img_head), (rx, ry))
                elif i == len(positions) - 1:
                    if len(positions) >= 2:
                        prev_x, prev_y = positions[-2]
                        tdx = max(-1, min(1, prev_x - cx))
                        tdy = max(-1, min(1, prev_y - cy))
                        tail_dir = (tdx, tdy)
                    screen.blit(tails.get(tail_dir, img_tail), (rx, ry))
                else:
                    screen.blit(img_body, (rx, ry))

            # D-pad overlay
            draw_dpad(screen, dpad_pos, BTN_R)

            # HUD
            diff_cfg = DIFFICULTIES[selected_diff]
            badge_w = 90
            draw_button(screen, 8, 8, badge_w, 28, diff_cfg["color"], alpha=185, radius=8)
            badge_txt = font_sm.render(diff_cfg["label"], True, (255, 255, 255))
            screen.blit(badge_txt, (8 + badge_w//2 - badge_txt.get_width()//2,
                                    8 + 14 - badge_txt.get_height()//2))

            hud = font_md.render("Score: " + str(score) + "   Length: " + str(snake.length),
                                 True, (190, 195, 210))
            screen.blit(hud, (badge_w + 18, 8))

            bonus_hud = font_sm.render("Bonus Moves Left: " + str(bonus_moves_left) +
                                       "   Bonus Points: +" + str(bonus_points_total),
                                       True, (140, 208, 150))
            screen.blit(bonus_hud, (badge_w + 18, 34))

            if is_paused:
                pause_overlay = pygame.Surface((W, H), pygame.SRCALPHA)
                pause_overlay.fill((0, 0, 0, 110))
                screen.blit(pause_overlay, (0, 0))

                p_title = font_lg.render("PAUSED", True, (245, 245, 245))
                screen.blit(p_title, (W//2 - p_title.get_width()//2, H//2 - 58))

                p_hint = font_sm.render("Tap Resume or press P to continue", True, (205, 210, 220))
                screen.blit(p_hint, (W//2 - p_hint.get_width()//2, H//2 + 2))

                draw_button(screen, resume_btn_rect.x, resume_btn_rect.y,
                            resume_btn_rect.w, resume_btn_rect.h,
                            (60, 180, 60), alpha=200, radius=10)
                resume_txt = font_md.render("RESUME", True, (255, 255, 255))
                screen.blit(resume_txt, (resume_btn_rect.x + resume_btn_rect.w//2 - resume_txt.get_width()//2,
                                         resume_btn_rect.y + resume_btn_rect.h//2 - resume_txt.get_height()//2))

                draw_button(screen, pause_menu_btn_rect.x, pause_menu_btn_rect.y,
                            pause_menu_btn_rect.w, pause_menu_btn_rect.h,
                            (80, 95, 180), alpha=190, radius=10)
                pause_menu_txt = font_md.render("BACK TO MENU", True, (255, 255, 255))
                screen.blit(pause_menu_txt,
                            (pause_menu_btn_rect.x + pause_menu_btn_rect.w//2 - pause_menu_txt.get_width()//2,
                             pause_menu_btn_rect.y + pause_menu_btn_rect.h//2 - pause_menu_txt.get_height()//2))

            draw_pause_icon_button(screen, pause_btn_rect, is_paused)

        # ==========================================
        # RENDER: GAME OVER
        # ==========================================
        elif state == "gameover":
            screen.fill((15, 15, 25))
            diff_cfg = DIFFICULTIES[selected_diff]

            go = font_lg.render("GAME OVER", True, (220, 60, 60))
            screen.blit(go, (W//2 - go.get_width()//2, H//2 - 90))

            sc = font_md.render("Score: " + str(score) + "    Length: " + str(snake.length),
                                True, (200, 200, 210))
            screen.blit(sc, (W//2 - sc.get_width()//2, H//2 - 25))

            bonus_txt = font_sm.render("Bonus Points: +" + str(bonus_points_total) +
                                       "    Bonus Moves Left: " + str(bonus_moves_left),
                                       True, (155, 220, 170))
            screen.blit(bonus_txt, (W//2 - bonus_txt.get_width()//2, H//2 + 3))

            dt_txt = font_sm.render("Difficulty: " + diff_cfg["label"], True, diff_cfg["color"])
            screen.blit(dt_txt, (W//2 - dt_txt.get_width()//2, H//2 + 23))

            # Restart button
            draw_button(screen, W//2 - 100, H//2 + 50, 200, 52, (60, 180, 60), alpha=200)
            r = font_md.render("R  -  Restart", True, (255, 255, 255))
            screen.blit(r, (W//2 - r.get_width()//2,
                            H//2 + 50 + 26 - r.get_height()//2))

            # Menu button
            draw_button(screen, W//2 - 100, H//2 + 112, 200, 52, (60, 90, 180), alpha=180)
            m = font_md.render("M  -  Menu", True, (255, 255, 255))
            screen.blit(m, (W//2 - m.get_width()//2,
                            H//2 + 112 + 26 - m.get_height()//2))

        pygame.display.flip()
        await asyncio.sleep(0)   # Required for Pygbag web compatibility


if __name__ == "__main__":
    asyncio.run(main())