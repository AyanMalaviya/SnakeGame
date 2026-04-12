@echo off
REM Windows Builder + Package Script for Linked List Snake
REM This script creates a Windows standalone executable using PyInstaller
REM Run this in Command Prompt or PowerShell

echo =========================================
echo Building Linked List Snake for Windows
echo =========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Step 1: Installing PyInstaller...
pip install pyinstaller --upgrade -q
if errorlevel 1 (
    echo Error: Failed to install PyInstaller
    pause
    exit /b 1
)

echo Step 2: Cleaning previous builds...
rmdir /s /q build dist *.spec 2>nul

echo Step 3: Building executable with PyInstaller...
pyinstaller ^
    --name="Linked List Snake" ^
    --onefile ^
    --windowed ^
    --hidden-import=pygame ^
    --add-data="apple.png;." ^
    --icon=snake-icon.ico ^
    main.py

if errorlevel 1 (
    echo Error: PyInstaller build failed
    pause
    exit /b 1
)

echo.
echo =========================================
echo Executable created successfully!
echo Location: dist\Linked List Snake.exe
echo =========================================
echo.
echo You can now:
echo   1. Run the game: dist\Linked List Snake.exe
echo   2. Distribute the .exe file to others (no installation needed)
echo   3. Create a shortcut on your desktop
echo.
pause
