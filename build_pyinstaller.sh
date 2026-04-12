#!/bin/bash
# PyInstaller-based build script for Linked List Snake
# This method is more reliable and creates standalone executables for both Windows and Linux

set -e

echo "Building Linked List Snake with PyInstaller..."
echo "=============================================="

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Clean previous builds
rm -rf build dist *.spec

# Create basic icon placeholder if it doesn't exist
if [ ! -f "snake-icon.png" ]; then
    echo "Note: No snake-icon.png found. App will use default icon."
fi

# Build with PyInstaller
echo "Building executable..."
pyinstaller \
    --name="Linked List Snake" \
    --windowed \
    --onefile \
    --hidden-import=pygame \
    --add-data="apple.png:." \
    main.py

echo "=============================================="
echo "Build complete!"
echo "Executable location: dist/Linked\ List\ Snake"
echo ""
echo "For AppImage creation (Linux):"
echo "  1. Install linuxdeploy: https://github.com/linuxdeploy/linuxdeploy"
echo "  2. Run: linuxdeploy-x86_64.AppImage --appdir=AppDir -e dist/Linked\ List\ Snake -d linked-list-snake.desktop -i snake-icon.png --output=appimage"
