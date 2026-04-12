# Hizzz Snake Game

A visually stunning Snake game written in Python with Pygame, featuring a doubly-linked list data structure for game mechanics. Fully compatible with both Windows and Linux.

## Features

- 🐍 Classic snake gameplay with modern visuals
- 👥 **2-Player Local Multiplayer** - Play on the same device (no hosting/server)
- 🎮 Three difficulty levels (Easy, Medium, Hard)
- 🎨 Beautiful gradient graphics and animations
- ⌨️ Extended keyboard controls (Arrow, WASD, Numpad, IJKL)
- 📱 Mobile-friendly D-pad controls and swipe support
- ⚙️ Cross-platform compatibility (Windows & Linux)
- 💾 Optimized data structures (Doubly-Linked List)

## System Requirements

- Python 3.8+
- pygame >= 2.1.0
- 64-bit system (for AppImage)

## Installation

### Quick Start (Any OS)

1. **Clone or download the repository**
   ```bash
   cd SnakeGame
   ```

2. **Install dependencies**
   ```bash
   pip install pygame
   ```

3. **Run the game**
   ```bash
   # New: Use main_multiplayer.py for bundled single + multiplayer modes
   python3 main_multiplayer.py
   
   # Or run single-player only:
   python3 main.py
   ```

### Multiplayer Mode

This project now uses **local multiplayer only** (no host/join/server setup).

Run:
```bash
python3 main_multiplayer.py
```

Then select:
- **SINGLE PLAYER**
- **LOCAL MULTIPLAYER**

In local multiplayer:
- Player 1 uses Arrow Keys or Numpad `8` `4` `2` `6`
- Player 2 uses `W` `A` `S` `D` or `I` `J` `K` `L`
- Snakes spawn from clockwise corners (ready for future 4-player expansion)
- 3-minute match, winner is highest peak length (no multiplayer points)
- Apple eaten with exactly 1 input gap grants extra length

See [MULTIPLAYER_GUIDE.md](MULTIPLAYER_GUIDE.md) for details.

### Linux

#### Method 1: Direct Execution
```bash
pip install pygame
python3 main.py
```

#### Method 2: AppImage (Recommended for Distribution)

AppImage is a portable format that works on any Linux distribution without installation.

##### Prerequisites

Install linuxdeploy (easier method) or appimagetool:
```bash
# Using linuxdeploy (recommended)
wget https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
chmod +x linuxdeploy-x86_64.AppImage

# OR using appimagetool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool
```

##### Build AppImage with PyInstaller + linuxdeploy (Easiest)

```bash
# 1. Install build tools
pip install pyinstaller pygame

# 2. Build with PyInstaller
pyinstaller --onefile --windowed --hidden-import=pygame main_multiplayer.py

# 3. Create AppImage using provided script
bash build_appimage_linuxdeploy.sh
```

##### Manual AppImage Creation Steps

1. **Create AppImage directory structure:**
   ```bash
   mkdir -p AppDir/usr/{bin,lib/python3.11/site-packages,share/applications,share/pixmaps}
   ```

2. **Install Python dependencies:**
   ```bash
   python3 -m pip install --target=AppDir/usr/lib/python3.11/site-packages pygame
   ```

3. **Copy game files:**
   ```bash
   cp main.py AppDir/
   cp apple.png AppDir/ 2>/dev/null || true
   cp linked-list-snake.desktop AppDir/usr/share/applications/
   cp snake-icon.png AppDir/usr/share/pixmaps/ 2>/dev/null || true
   ```

4. **Copy AppRun script:**
   ```bash
   cp AppRun AppDir/
   chmod +x AppDir/AppRun
   ```

5. **Create the AppImage:**
   ```bash
   appimagetool -n AppDir Linked_List_Snake-x86_64.AppImage
   chmod +x Linked_List_Snake-x86_64.AppImage
   ```

6. **Run the AppImage:**
   ```bash
   ./Linked_List_Snake-x86_64.AppImage
   ```

## Controls

### Keyboard Controls
- **Single Player**: Arrow Keys or WASD
- **Local Multiplayer P1**: Arrow Keys or Numpad `8` `4` `2` `6`
- **Local Multiplayer P2**: `W` `A` `S` `D` or `I` `J` `K` `L`
- **P** - Pause/Resume
- **ESC** - Back to menu
- **R** - Restart (game over screen)

### Mouse/Touch Controls  
- **D-Pad** - Mobile direction control
- **Swipe** - Gesture-based movement (mobile)
- **Buttons** - UI interactions

## Game Mechanics

### Scoring
- Eat apples: **+10 points** (×difficulty multiplier)
- Combo bonus (input-based):
   - Next apple within 1 input: **+20**
   - Next apple within 2 inputs: **+10**
   - Next apple within 3 inputs: **+5**
- Difficulty multipliers:
  - Easy: 1×
  - Medium: 2×
  - Hard: 3×

### Collision Rules
- Hitting stones → Game Over
- Hitting your own body → Game Over
- Multiplayer head-to-body bite → bitten snake is cut from bite point, biter gains pending length
- Multiplayer head-to-head clash → both snakes are reduced to half length
- Multiplayer stone/self collision → that snake is reduced to half length
- Screen wraps around (portals on edges)

### Data Structure
The snake uses a **doubly-linked list** implementation:
- O(1) head insertion for smooth movement
- O(1) tail removal (no resizing)
- Efficient body collision detection
- Smooth interpolation for visual feedback

## Configuration Files

- `setup.py` - Package configuration
- `linked-list-snake.desktop` - Linux desktop integration
- `AppRun` - AppImage runtime script
- `pygbag.ini` - Web build configuration

## Package as Distribution

### For Linux (Create Portable AppImage)
```bash
chmod +x build_appimage_linuxdeploy.sh
./build_appimage_linuxdeploy.sh
# Creates: Linked_List_Snake-x86_64.AppImage
```

### For Windows (Build From Project Venv)
```bat
cd game
build_windows_exe.bat
```

This creates `dist\Hizzz Snake.exe` and uses `..\venv\Scripts\pyinstaller.exe`.

## Troubleshooting

### "pygame not found"
```bash
pip install pygame --upgrade
```

### Black screen on Linux
- Try setting SDL video driver: `SDL_VIDEODRIVER=x11 python3 main.py`
- Or: `SDL_VIDEODRIVER=wayland python3 main.py`

### AppImage won't run
```bash
./Linked_List_Snake-x86_64.AppImage --appimage-extract
cd squashfs-root
./AppRun
```

### Font issues
The game now uses cross-platform fonts: monospace, DejaVu Sans Mono, Courier New, and Consolas (as fallback).

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - feel free to use and modify

## Author

Created with ❤️ using Python and Pygame

---

**Happy gaming! 🎮**
