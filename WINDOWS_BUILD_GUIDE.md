# Windows Build Guide for Linked List Snake

## Quick Start (Easiest)

### Method 1: Use Python Script (Recommended)

```bash
python build_windows_exe.py
```

This will:
1. Install PyInstaller automatically
2. Build the executable
3. Create `dist\Linked List Snake.exe`

### Method 2: Use Batch Script

Double-click `build_windows_exe.bat` and follow the prompts.

---

## Building the EXE

### Prerequisites

- **Python 3.8+** - Download from https://www.python.org/
  - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation
- **pygame** - Will be compiled during build

### Step 1: Install PyInstaller

```cmd
pip install pyinstaller --upgrade
```

### Step 2: Run the Build

```cmd
python build_windows_exe.py
```

Or use the batch file:
```cmd
build_windows_exe.bat
```

### Step 3: Find Your Executable

The built .exe is located at: `dist\Linked List Snake.exe`

---

## Distributing Your Game

### Standalone EXE
- Simply copy `dist\Linked List Snake.exe` to any Windows computer
- No Python installation required (all dependencies are bundled)
- File size: ~80-100 MB

### Create Windows Installer (Optional)

1. **Download NSIS** from https://nsis.sourceforge.io/
2. Right-click `linked-list-snake-installer.nsi`
3. Select **"Compile NSIS Script"**
4. This creates `Linked_List_Snake_Installer.exe`

Users can then:
- Run the installer to install the game
- Create Start Menu shortcuts
- Create Desktop shortcut
- Easy uninstall via Control Panel

---

## Troubleshooting

### "Python is not installed or not in PATH"

**Solution:**
1. Reinstall Python from https://www.python.org/
2. ✅ Check **"Add Python to PATH"** during installation
3. Restart Command Prompt/PowerShell
4. Try again

### "PyInstaller not found"

**Solution:**
```cmd
pip install pyinstaller
```

### ".exe won't run"

**Solutions:**
1. Make sure pygame was installed during build
2. Try building again: `python build_windows_exe.py`
3. Check that `apple.png` exists in the project folder

### Antivirus warns about .exe

**This is normal!** PyInstaller-built executables sometimes trigger antivirus warnings because:
- They bundle Python and dependencies
- They extract to a temporary folder at runtime

**Solution:** Add the game folder to your antivirus whitelist, or build an official installer with NSIS (above).

---

## Creating a Desktop Shortcut

1. Build the exe: `python build_windows_exe.py`
2. Navigate to `dist` folder
3. Right-click `Linked List Snake.exe`
4. Select "Create shortcut"
5. Move shortcut to Desktop

---

## Building for Different Architectures

### 64-bit (Default, Recommended)
```cmd
python build_windows_exe.py
```

### 32-bit
```cmd
python -c "import struct; print(struct.calcsize('P') * 8)" REM Check your currently running Python
```

If you need 32-bit:
1. Install 32-bit Python from https://www.python.org/downloads/
2. Use that Python version to build

---

## Advanced: Customizing the Build

Edit `build_windows_exe.py` to:

- Change icon: Modify `--icon=snake-icon.ico` to use your icon
- Add files: Add `--add-data=filename:dest_folder`
- Change console behavior: Remove `--windowed` for console window
- Optimize size: Add `--upx` option (requires UPX installation)

---

## Tips for Distribution

### Size Optimization
- Default build: ~80-100 MB
- To reduce size, you could:
  - Split pygame components
  - Use pygame-ce (community edition)
  - Compress with 7-Zip before distribution

### Version Updates
1. Modify game code
2. Update version in code comments
3. Run `python build_windows_exe.py` again
4. New .exe is ready to distribute

### Code Signing (Professional)
For enterprise distribution, consider code signing your .exe:
- Uses digital certificate
- Removes antivirus warnings
- Requires code signing certificate

---

## One-Click Distribution Package

To create a complete distribution:

```cmd
# Build everything
python build_windows_exe.py

# Create installer (optional, requires NSIS)
makensis.exe linked-list-snake-installer.nsi

# Now you have:
# - dist\Linked List Snake.exe (standalone)
# - Linked_List_Snake_Installer.exe (with installer)
```

Both can be distributed to users!
