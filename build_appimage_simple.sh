#!/bin/bash
# Simple AppImage builder - Downloads tools if needed

set -e

echo "======================================"
echo "Building AppImage - Simple Method"
echo "======================================"

# Check if executable exists
if [ ! -f "dist/Linked_List_Snake" ]; then
    echo "Building executable with PyInstaller..."
    pip install pyinstaller -q
    # Use main_multiplayer.py for embedded server support
    python3 -m PyInstaller \
        --name="Linked_List_Snake" \
        --onefile \
        --windowed \
        --hidden-import=pygame \
        --add-data="apple.png:." \
        main_multiplayer.py
    echo "✓ Executable created: dist/Linked_List_Snake"
fi

# Download appimagetool if needed
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo "Downloading appimagetool..."
    wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
    echo "✓ appimagetool downloaded"
fi

# Create AppImage directory structure
echo "Creating AppImage structure..."
rm -rf Linked_List_Snake.AppDir
mkdir -p Linked_List_Snake.AppDir/usr/{bin,share/{applications,pixmaps}}

# Copy executable
cp dist/Linked_List_Snake Linked_List_Snake.AppDir/usr/bin/

# Copy assets
if [ -f "apple.png" ]; then
    cp apple.png Linked_List_Snake.AppDir/
fi

# Copy icon files for AppImage
if [ -f "favicon.png" ]; then
    cp favicon.png Linked_List_Snake.AppDir/snake-icon.png
    cp favicon.png Linked_List_Snake.AppDir/usr/share/pixmaps/snake-icon.png
fi

# Copy desktop file (both to root and applications folder for compatibility)
cp linked-list-snake.desktop Linked_List_Snake.AppDir/
cp linked-list-snake.desktop Linked_List_Snake.AppDir/usr/share/applications/

# Create AppRun script
cat > Linked_List_Snake.AppDir/AppRun << 'EOF'
#!/bin/bash
APPDIR="$(dirname "$(readlink -f "$0")")"
exec "$APPDIR/usr/bin/Linked_List_Snake" "$@"
EOF
chmod +x Linked_List_Snake.AppDir/AppRun

# Build AppImage
echo "Creating AppImage..."
./appimagetool-x86_64.AppImage -n Linked_List_Snake.AppDir Linked_List_Snake-x86_64.AppImage

chmod +x Linked_List_Snake-x86_64.AppImage

# Cleanup
rm -rf Linked_List_Snake.AppDir

echo ""
echo "======================================"
echo "✓ AppImage created successfully!"
echo "======================================"
echo ""
echo "Run with: ./Linked_List_Snake-x86_64.AppImage"
