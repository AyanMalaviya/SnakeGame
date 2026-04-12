#!/usr/bin/env python3
"""
Two-player multiplayer game logic for Snake Rush.

Rules implemented here:
- Head-on-body: bitten snake is cut at bite point.
- Head-to-head: both snakes are reduced to half length.
"""

from typing import Optional, Tuple

class MultiplayerGameLogic:
    """Helpers for local multiplayer collision and length updates."""

    @staticmethod
    def get_body_hit_index(
        attacker_head: Tuple[int, int],
        victim_positions: list,
    ) -> Optional[int]:
        """
        Return the victim body index hit by attacker head.

        Index is in victim_positions (head=0). Returns None if no body hit.
        """
        for idx, segment in enumerate(victim_positions[1:], start=1):
            if attacker_head == segment:
                return idx
        return None

    @staticmethod
    def trim_snake_to_length(snake, keep_length: int) -> int:
        """
        Trim snake to keep_length and return removed segment count.

        keep_length is clamped to at least 1.
        """
        if keep_length < 1:
            keep_length = 1
        if keep_length >= snake.length:
            return 0

        cursor = snake.head
        for _ in range(keep_length - 1):
            if cursor.next is None:
                break
            cursor = cursor.next

        removed = snake.length - keep_length

        # Keep only the first keep_length nodes.
        cursor.next = None
        snake.tail = cursor
        snake.length = keep_length
        return removed

    @staticmethod
    def apply_head_collision_halving(snake_a, snake_b) -> bool:
        """
        Apply head-to-head rule: both snakes become half length.

        Returns True when a head-to-head collision happened.
        """
        a_head = (snake_a.head.x, snake_a.head.y)
        b_head = (snake_b.head.x, snake_b.head.y)
        if a_head != b_head:
            return False

        MultiplayerGameLogic.trim_snake_to_length(snake_a, max(1, snake_a.length // 2))
        MultiplayerGameLogic.trim_snake_to_length(snake_b, max(1, snake_b.length // 2))
        return True

    @staticmethod
    def check_self_collision(body_positions: list) -> bool:
        """Check if snake collided with itself"""
        if len(body_positions) < 2:
            return False

        head = body_positions[0]
        for segment in body_positions[1:]:
            if head == segment:
                return True
        return False

    @staticmethod
    def check_stone_collision(head_pos: Tuple[int, int], stones: set) -> bool:
        """Check if head hit a stone"""
        return head_pos in stones

    @staticmethod
    def can_eat_apple(head_pos: Tuple[int, int], apple_pos: Tuple[int, int]) -> bool:
        """Check if head ate apple"""
        return head_pos == apple_pos
