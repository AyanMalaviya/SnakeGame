# Linked List Snake Game

A visually stunning Snake game written in Python with Pygame, featuring a doubly-linked list data structure for game mechanics. Fully compatible with both Windows and Linux.

## Features

- 🐍 Classic snake gameplay with modern visuals
- 👥 **NEW: 2-Player Multiplayer** - Play online with a friend!
- 🎮 Three difficulty levels (Easy, Medium, Hard)
- 🎨 Beautiful gradient graphics and animations
- ⌨️ Keyboard controls (Arrow Keys / WASD)
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
   python main.py
   ```

### Multiplayer Mode

To play with a friend online:

**NEW! Quick Start:**
```bash
# Terminal 1: Start the multiplayer server
bash start_multiplayer_server.sh

# Terminal 2: Launch the game with multiplayer menu
python3 main_multiplayer.py
```

Then from the menu:
- **Host A Game**: Create a session (other players join you)
- **Join A Game**: Connect to someone's session
- **Single Player**: Play the original game

**Full Details:** See [MULTIPLAYER_SETUP.md](MULTIPLAYER_SETUP.md)

**For Developers:** See [MULTIPLAYER_GUIDE.md](MULTIPLAYER_GUIDE.md) and [MULTIPLAYER_IMPLEMENTATION.md](MULTIPLAYER_IMPLEMENTATION.md)

### Windows

#### Method 1: Direct Execution
```bash
pip install pygame
python main.py
```

#### Method 2: PyInstaller Executable
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --hidden-import=pygame main.py
# Run the .exe from dist/ folder
```

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
pyinstaller --onefile --windowed --hidden-import=pygame main.py

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
- **Arrow Keys** or **WASD** - Move snake
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
- Combo bonus: +1 point for eating 2 apples within 3 moves
- Difficulty multipliers:
  - Easy: 1×
  - Medium: 2×
  - Hard: 3×

### Collision Rules
- Hitting stones → Game Over
- Hitting your own body → Game Over
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

### For Windows (Create Standalone EXE)

**Quick Method:**
```bash
python build_windows_exe.py
```

This creates `dist\Linked List Snake.exe` - a standalone executable that needs no installation!

**Or use Batch Script:**
Double-click `build_windows_exe.bat`

**Full Guide:** See [WINDOWS_BUILD_GUIDE.md](WINDOWS_BUILD_GUIDE.md)

**Optional: Create Windows Installer**
1. Download NSIS from https://nsis.sourceforge.io/
2. Right-click `linked-list-snake-installer.nsi`
3. Select "Compile NSIS Script"
4. Creates `Linked_List_Snake_Installer.exe`

### For macOS
```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
# Creates standalone .app bundle in dist/ folder
```

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
