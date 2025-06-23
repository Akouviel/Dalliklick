#!/bin/bash

# Dalli Klick 2025 - Stable Version für macOS 14.7.6
# Verwendet Python 3.11.9 für Stabilität (keine Abort trap: 6 Crashes)

echo "🎮 Starting Dalli Klick 2025 (Stable Version)..."
echo "🐍 Using Python 3.11.9 (stable version)"
echo "🛡️ No crashes - optimized for macOS 14.7.6"
echo "========================================"

# Setze das Arbeitsverzeichnis
GAME_DIR="$HOME/Desktop/Dalliklick"
cd "$GAME_DIR"

# Prüfe ob das Verzeichnis existiert
if [ ! -d "$GAME_DIR" ]; then
    echo "❌ Game directory not found: $GAME_DIR"
    echo "Creating directory..."
    mkdir -p "$GAME_DIR"
    echo "✅ Directory created: $GAME_DIR"
    echo "Please copy your game file dalli_klick_2025.py to this directory."
    echo ""
    read -n 1 -s -r -p "Press any key to exit..."
    exit 1
fi

# Prüfe ob Python 3.11.9 verfügbar ist
if ! command -v python3.11 &> /dev/null; then
    echo "❌ Python 3.11.9 not found!"
    echo "Please install Python 3.11.9 from: https://www.python.org/downloads/release/python-3119/"
    echo ""
    read -n 1 -s -r -p "Press any key to exit..."
    exit 1
fi

# Zeige Python-Version
echo "🐍 Python version: $(python3.11 --version)"

# Prüfe ob das Spiel existiert
if [ ! -f "dalli_klick_2025.py" ]; then
    echo "❌ Game file dalli_klick_2025.py not found!"
    echo "Please ensure the file is in: $GAME_DIR"
    echo ""
    echo "Files in current directory:"
    ls -la
    echo ""
    read -n 1 -s -r -p "Press any key to exit..."
    exit 1
fi

# Prüfe ob virtuelles Environment existiert
if [ ! -d "venv311" ]; then
    echo "🔧 Creating virtual environment with Python 3.11.9..."
    python3.11 -m venv venv311
    echo "✅ Virtual environment created"
fi

# Aktiviere virtuelles Environment
echo "🔧 Activating virtual environment..."
source venv311/bin/activate

# Prüfe ob pygame installiert ist
if ! python -c "import pygame" &> /dev/null; then
    echo "🔧 Installing pygame..."
    pip install pygame
    echo "✅ Pygame installed"
else
    echo "✅ Pygame already installed"
fi

# Alles bereit
echo ""
echo "✅ Everything is ready!"
echo "🚀 Starting the game with Python 3.11.9..."
echo "💡 Tip: Press ESC in the game for menu"
echo "🛡️ This version is stable on macOS 14.7.6!"
echo "========================================"
echo ""

# Starte das Spiel mit Python 3.11.9
python dalli_klick_2025_fixed.py

# Behalte das Terminal offen nach dem Spiel
echo ""
echo "🎮 Game ended. Press any key to close..."
read -n 1 -s -r

cd "$(dirname "$0")"

# Activate venv311 if it exists
if [ -d "venv311" ]; then
  source venv311/bin/activate
fi

# Install requirements if needed
pip3 install --quiet -r requirements.txt

# Run the game
python3 dalli_klick_2025_fixed.py

# Keep terminal open after game
read -n 1 -s -r -p "Game ended. Press any key to exit..." 