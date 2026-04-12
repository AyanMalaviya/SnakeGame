#!/bin/bash
# Build AppImage using linuxdeploy (Most reliable method)
# This script creates a portable AppImage for Linux

set -e

echo "===================================="
echo "Building Linked List Snake AppImage"
echo "===================================="

# Check for required tools
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

if ! command -v pip &> /dev/null; then
    echo "Error: pip is not installed"
    exit 1
fi

# Install PyInstaller if needed
if ! python3 -m pip show pyinstaller &>/dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

echo "Step 1: Building executable with PyInstaller..."
rm -rf build/ dist/ *.spec
python3 -m PyInstaller \
    --name="Linked_List_Snake" \
    --onefile \
    --windowed \
    --hidden-import=pygame \
    --add-data="apple.png:." \
    main.py

if [ ! -f "dist/Linked_List_Snake" ]; then
    echo "Error: PyInstaller build failed"
    exit 1
fi

echo "Step 2: Preparing AppImage structure..."

# Create AppImage structure
mkdir -p "Linked_List_Snake.AppDir/usr/bin"
mkdir -p "Linked_List_Snake.AppDir/usr/share/applications"
mkdir -p "Linked_List_Snake.AppDir/usr/share/pixmaps"

# Copy executable
cp "dist/Linked_List_Snake" "Linked_List_Snake.AppDir/usr/bin/"

# Copy desktop file
cp "linked-list-snake.desktop" "Linked_List_Snake.AppDir/usr/share/applications/"

# Copy icon if available
if [ -f "snake-icon.png" ]; then
    cp "snake-icon.png" "Linked_List_Snake.AppDir/usr/share/pixmaps/"
fi

# Create AppRun script
cat > "Linked_List_Snake.AppDir/AppRun" << 'EOF'
#!/bin/bash
APPDIR="$(dirname "$(readlink -f "$0")")"
exec "$APPDIR/usr/bin/Linked_List_Snake" "$@"
EOF
chmod +x "Linked_List_Snake.AppDir/AppRun"

# Check if linuxdeploy is available
if command -v linuxdeploy &> /dev/null; then
    echo "Step 3: Running linuxdeploy..."
    linuxdeploy --appdir="Linked_List_Snake.AppDir" \
        --output=appimage
    
    # Rename the output
    if [ -f "Linked_List_Snake-x86_64.AppImage" ]; then
        chmod +x "Linked_List_Snake-x86_64.AppImage"
        echo "===================================="
        echo "✓ AppImage created successfully!"
        echo "Run: ./Linked_List_Snake-x86_64.AppImage"
        echo "===================================="
    fi
else
    echo "Warning: linuxdeploy not found. Trying appimagetool..."
    
    if command -v appimagetool &> /dev/null; then
        appimagetool -n "Linked_List_Snake.AppDir" "Linked_List_Snake-x86_64.AppImage"
        chmod +x "Linked_List_Snake-x86_64.AppImage"
        echo "===================================="
        echo "✓ AppImage created successfully!"
        echo "Run: ./Linked_List_Snake-x86_64.AppImage"
        echo "===================================="
    else
        echo "Error: Neither linuxdeploy nor appimagetool found"
        echo "Install linuxdeploy from: https://github.com/linuxdeploy/linuxdeploy"
        exit 1
    fi
fi

# Cleanup
echo "Cleaning up..."
rm -rf "Linked_List_Snake.AppDir"

echo "Done!"
