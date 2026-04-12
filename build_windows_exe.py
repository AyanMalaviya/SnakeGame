#!/usr/bin/env python3
"""
Windows EXE Builder for Linked List Snake
Run: python build_windows_exe.py
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and exit if it fails"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False)
        if result.returncode != 0:
            print(f"❌ Error: {description} failed")
            sys.exit(1)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def main():
    print("=" * 50)
    print("Building Linked List Snake for Windows")
    print("=" * 50)
    
    # Check Python
    print("\n✓ Python version:", sys.version.split()[0])
    
    # Check if pygame is installed
    try:
        import pygame
        print(f"✓ pygame version: {pygame.__version__}")
    except ImportError:
        print("⚠️  pygame not found, installing...")
        run_command("pip install pygame", "Installing pygame")
    
    # Install PyInstaller
    run_command("pip install pyinstaller --upgrade -q", "Installing PyInstaller")
    
    # Clean previous builds
    print("\n🧹 Cleaning previous builds...")
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
    
    # Build with PyInstaller
    icon_arg = '--icon=snake-icon.ico' if os.path.exists('snake-icon.ico') else ''
    apple_arg = '--add-data=apple.png:.' if os.path.exists('apple.png') else ''
    
    cmd = f'''pyinstaller \
        --name="Linked List Snake" \
        --onefile \
        --windowed \
        --hidden-import=pygame \
        {apple_arg} \
        {icon_arg} \
        main.py'''
    
    run_command(cmd, "Building executable")
    
    # Check if build was successful
    exe_path = Path('dist') / 'Linked List Snake.exe'
    if exe_path.exists():
        print("\n" + "=" * 50)
        print("✓ Build successful!")
        print("=" * 50)
        print(f"\nExecutable location: dist\\Linked List Snake.exe")
        print(f"File size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
        print("\nYou can now:")
        print("  1. Run the game: dist\\Linked List Snake.exe")
        print("  2. Distribute the .exe file to others")
        print("  3. Create a Windows installer (optional)")
    else:
        print("\n❌ Build failed: .exe file not created")
        sys.exit(1)

if __name__ == '__main__':
    main()
