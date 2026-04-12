@echo off
REM Start multiplayer server for Linked List Snake on Windows

echo ======================================
echo Linked List Snake - Multiplayer Server
echo ======================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Default port
set PORT=9999
set HOST=0.0.0.0

if not "%1"=="" set PORT=%1
if not "%2"=="" set HOST=%2

echo Starting server on %HOST%:%PORT%...
echo.
echo Server details:
echo   Host: %HOST%
echo   Port: %PORT%
echo   Local: localhost:%PORT%
echo.
echo To join from another computer:
echo   - Make sure port %PORT% is open in firewall
echo   - Use server IP ^(find with: ipconfig^)
echo   - Example: 192.168.1.100:%PORT%
echo.
echo Press Ctrl+C to stop server
echo.

python3 -c "import sys; sys.path.insert(0, '.'); from multiplayer_server import MultiplayerServer; server = MultiplayerServer(host='%HOST%', port=%PORT%); server.start()"

pause
