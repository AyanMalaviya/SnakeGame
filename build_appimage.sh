#!/bin/bash
# Build script for creating Linked List Snake AppImage
# Run this script on Linux to create a distributable AppImage

set -e

echo "Building Linked List Snake AppImage..."
echo "======================================="

# Check dependencies
command -v appimagetool >/dev/null 2>&1 || {
    echo "Error: appimagetool is not installed."
    echo "Install it with: wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    echo "Then: chmod +x appimagetool-x86_64.AppImage && sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool"
    exit 1
}

# Create AppImage directory structure
APPDIR="Linked_List_Snake.AppDir"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/lib"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/pixmaps"

echo "Setting up AppImage directory..."

# Copy game files (use main_multiplayer.py for embedded server support)
cp main_multiplayer.py "$APPDIR/main_multiplayer.py"
# Also copy main.py as it's imported by main_multiplayer.py
cp main.py "$APPDIR/main.py"
if [ -f "apple.png" ]; then
    cp apple.png "$APPDIR/apple.png"
fi

# Copy desktop entry
cp linked-list-snake.desktop "$APPDIR/usr/share/applications/"

# Create a simple icon (if you have one)
if [ -f "snake-icon.png" ]; then
    cp snake-icon.png "$APPDIR/usr/share/pixmaps/"
fi

# Install Python and dependencies into AppImage
echo "Installing Python and dependencies..."
python3 -m pip install --target="$APPDIR/usr/lib/python3.11/site-packages" pygame==2.5.2

# Copy Python interpreter
cp "$(which python3)" "$APPDIR/usr/bin/python3" || echo "Warning: Could not copy python3"

# Copy necessary libraries
for lib in libpython3.11.so.1.0 libpython3.so libc.so.6 libm.so.6; do
    if [ -f "/lib/x86_64-linux-gnu/$lib" ]; then
        cp "/lib/x86_64-linux-gnu/$lib" "$APPDIR/usr/lib/" 2>/dev/null || true
    fi
done

# Copy AppRun script
cp AppRun "$APPDIR/"
chmod +x "$APPDIR/AppRun"

# Create AppImage
echo "Creating AppImage..."
appimagetool -n "$APPDIR" "Linked_List_Snake-x86_64.AppImage"

# Make it executable
chmod +x "Linked_List_Snake-x86_64.AppImage"

# Cleanup
echo "Cleaning up..."
rm -rf "$APPDIR"

echo "======================================="
echo "AppImage created successfully!"
echo "Run with: ./Linked_List_Snake-x86_64.AppImage"
