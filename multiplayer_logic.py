#!/usr/bin/env python3
"""
Two-player multiplayer game logic for Linked List Snake
Handles collision detection, scoring, and multiplayer-specific rules
"""

import math
from typing import Tuple, Optional

class MultiplayerGameLogic:
    """Handles two-player game logic and collision detection"""

    @staticmethod
    def check_head_collision(p1_head: Tuple[int, int], p2_head: Tuple[int, int]) -> Tuple[bool, bool]:
        """
        Check head-to-head collision
        Returns: (p1_dies, p2_dies)
        """
        if p1_head == p2_head:
            # Both heads collide → both die
            return (True, True)
        return (False, False)

    @staticmethod
    def check_head_body_collision(
        head_pos: Tuple[int, int],
        body_positions: list,
        head_direction: Tuple[int, int]
    ) -> Optional[str]:
        """
        Check if head collided with body
        Returns: 'front' if collision with front face, 'side' if side collision, None if no collision
        """
        if not body_positions:
            return None

        for i, segment in enumerate(body_positions[:-1]):  # Skip tail
            if head_pos == segment:
                # Check if it's front face or side collision
                if i == 0:  # Head of body (front face)
                    return 'front'
                else:
                    # Check direction to determine if it's side collision
                    return 'side'
        return None

    @staticmethod
    def evaluate_multiplayer_collision(
        p1_head: Tuple[int, int],
        p1_body: list,
        p1_direction: Tuple[int, int],
        p2_head: Tuple[int, int],
        p2_body: list,
        p2_direction: Tuple[int, int],
        cols: int,
        rows: int
    ) -> Tuple[bool, bool, Optional[str]]:
        """
        Evaluate all collisions in two-player mode
        Returns: (p1_dies, p2_dies, collision_type)
        
        Collision types:
        - 'head_collision': both heads collide → both die
        - 'p1_eats_p2_tail': p1 dies (ate p2's tail)
        - 'p2_eats_p1_tail': p2 dies (ate p1's tail)
        - 'p1_front_p2_side': p2 dies (p1 hits p2's front face)
        - 'p2_front_p1_side': p1 dies (p2 hits p1's front face)
        - None: no collision
        """

        # Rule 1: Head-to-head collision
        head_collision = p1_head == p2_head
        if head_collision:
            return (True, True, 'head_collision')

        # Rule 2: Head eating opponent's tail
        if p1_head == p2_body[-1]:  # p1 ate p2's tail
            return (False, True, 'p1_eats_p2_tail')

        if p2_head == p1_body[-1]:  # p2 ate p1's tail
            return (True, False, 'p2_eats_p1_tail')

        # Rule 3: Head-to-body collision (front vs side)
        # Check if p1's head hit p2's body
        p2_collision = MultiplayerGameLogic.check_head_body_collision(p1_head, p2_body, p1_direction)
        if p2_collision == 'front':
            # p1 hit p2's front face → p2 dies
            return (False, True, 'p1_front_p2_front')
        elif p2_collision == 'side':
            # p1 hit p2's side → p1 dies
            return (True, False, 'p1_side_p2_body')

        # Check if p2's head hit p1's body
        p1_collision = MultiplayerGameLogic.check_head_body_collision(p2_head, p1_body, p2_direction)
        if p1_collision == 'front':
            # p2 hit p1's front face → p1 dies
            return (True, False, 'p2_front_p1_front')
        elif p1_collision == 'side':
            # p2 hit p1's side → p2 dies
            return (False, True, 'p2_side_p1_body')

        return (False, False, None)

    @staticmethod
    def determine_winner(
        p1_length: int,
        p2_length: int,
        p1_alive: bool,
        p2_alive: bool,
        killer_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Determine the winner based on game end conditions
        
        Rules:
        - If one player killed the other: killer wins
        - If both died same time: longer player wins
        - If one died: other wins
        """
        if killer_id:
            return killer_id

        if not p1_alive and not p2_alive:
            # Both dead → longer player wins
            return 'p1' if p1_length > p2_length else 'p2'

        if not p1_alive:
            return 'p2'

        if not p2_alive:
            return 'p1'

        return None

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
