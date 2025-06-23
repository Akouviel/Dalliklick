#!/bin/bash

cd "$(dirname "$0")"

# Activate venv if it exists
if [ -d ".venv" ]; then
  source venv/bin/activate
fi

# Install requirements if needed
pip3 install --quiet -r requirements.txt

# Run the game
python3 dalli_klick_2025_fixed.py

# Keep terminal open after game
echo "Game ended. Press any key to exit..."
read -n 1
