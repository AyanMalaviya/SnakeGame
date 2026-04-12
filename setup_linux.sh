#!/bin/bash
# Setup script for Linked List Snake on Fedora/Nobara

set -e

echo "========================================="
echo "Linked List Snake - Setup for Fedora/Nobara"
echo "========================================="
echo ""
echo "This script will install required dependencies for pygame."
echo "You will be prompted for your sudo password."
echo ""

# Install SDL2 development libraries
echo "Installing SDL2 and development headers..."
sudo dnf install -y \
    SDL2-devel \
    SDL2_image-devel \
    SDL2_ttf-devel \
    SDL2_mixer-devel \
    freetype-devel \
    python3-devel \
    pkg-config

echo ""
echo "✓ Development libraries installed!"
echo ""
echo "Now installing pygame..."
pip install pygame>=2.1.0 --upgrade

echo ""
echo "========================================="
echo "✓ Setup complete!"
echo "Run the game with: python3 main.py"
echo "========================================="
