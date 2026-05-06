#!/bin/bash
# Build script for macOS / Linux
set -e

echo "==> Bunny Fruit Frenzy: build script"

# Resolve script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Pick a Python
PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "Python 3 not found. Install Python 3.9+ first."
    exit 1
fi

echo "==> Using $($PYTHON --version)"

# Install deps
echo "==> Installing dependencies..."
"$PYTHON" -m pip install --upgrade pip >/dev/null
"$PYTHON" -m pip install -r requirements.txt
"$PYTHON" -m pip install pyinstaller

# Clean previous build
echo "==> Cleaning previous build..."
rm -rf build dist

# Build
echo "==> Running PyInstaller..."
"$PYTHON" -m PyInstaller BunnyFruitFrenzy.spec --noconfirm

echo ""
echo "==> Done!"
if [ -d "dist/BunnyFruitFrenzy.app" ]; then
    echo "    macOS app: dist/BunnyFruitFrenzy.app"
    echo "    Run it by double-clicking, or:  open dist/BunnyFruitFrenzy.app"
elif [ -f "dist/BunnyFruitFrenzy" ]; then
    echo "    Executable: dist/BunnyFruitFrenzy"
fi
