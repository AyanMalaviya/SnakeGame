# Multiplayer Guide (Local Only)

This game now supports **local multiplayer only**.
There is no host/join mode and no dedicated server process.

## How To Start

1. Run:
   ```bash
   python3 main_multiplayer.py
   ```
2. Choose `LOCAL MULTIPLAYER`.
3. Enter both player names and select difficulty.
4. Press `ENTER` to start.

## Controls

- Player 1: `Arrow Keys` or Numpad `8` `4` `2` `6`
- Player 2: `W` `A` `S` `D` or `I` `J` `K` `L`
- `ESC`: Back to menu

## Rules

- Both players share the same map, apple, and stones.
- Spawn points are aligned to clockwise corners (preparation for future 4-player mode).
- Match length is fixed: `3:00`.
- There is no point system in multiplayer. Winner is based on peak length.
- Each apple increases length.
- If a player eats the next apple with exactly `1` input between apples, that apple gives extra length.
- Snake-vs-snake rules:
  - Head-to-body bite: bitten snake is cut at the bite point.
  - The biting snake gains equivalent pending length growth.
  - Head-to-head clash: both snakes are reduced to half length.
- Additional penalty collisions:
  - Stone collision: snake is cut to half length
  - Self collision: snake is cut to half length
- Match ends when timer reaches `0:00`.

## Why Local Only?

The project is focused on stable packaging and gameplay for:
- Windows EXE
- Android build
- Linux build

So networking/hosting infrastructure was removed to keep builds simpler and more reliable.
