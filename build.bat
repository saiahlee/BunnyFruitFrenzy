@echo off
REM Build script for Windows
setlocal

echo ==^> Bunny Fruit Frenzy: build script

cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo Python not found. Install Python 3.9+ from python.org first.
    exit /b 1
)

echo ==^> Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

echo ==^> Cleaning previous build...
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist

echo ==^> Running PyInstaller...
python -m PyInstaller BunnyFruitFrenzy.spec --noconfirm

echo.
echo ==^> Done!
if exist dist\BunnyFruitFrenzy.exe (
    echo     Executable: dist\BunnyFruitFrenzy.exe
)
endlocal
