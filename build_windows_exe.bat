@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%"

set "VENV_PYINSTALLER=%SCRIPT_DIR%..\venv\Scripts\pyinstaller.exe"

if not exist "%VENV_PYINSTALLER%" (
    echo [ERROR] Could not find venv PyInstaller:
    echo         %VENV_PYINSTALLER%
    echo.
    echo Create/setup the project venv first, then install dependencies.
    popd
    exit /b 1
)

if not exist "main_multiplayer.py" (
    echo [ERROR] main_multiplayer.py not found in:
    echo         %SCRIPT_DIR%
    popd
    exit /b 1
)

echo Building Hizzz Snake EXE using project venv...
"%VENV_PYINSTALLER%" --noconfirm --clean --onefile --windowed --name "Hizzz Snake" --hidden-import=pygame --add-data "apple.png;." --icon "snake_icon.ico" --distpath dist --workpath build main_multiplayer.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed.
    popd
    exit /b 1
)

if exist "dist\Hizzz Snake.exe" (
    echo.
    echo [OK] Build complete:
    echo      %SCRIPT_DIR%dist\Hizzz Snake.exe
) else (
    echo.
    echo [WARN] Build command completed but EXE was not found at expected path.
)

popd
exit /b 0
