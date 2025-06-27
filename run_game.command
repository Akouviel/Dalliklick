#!/bin/zsh
cd "$(dirname "$0")"
source venv311/bin/activate
python3 dalli_klick_2025_fixed.py
echo
echo "Zum Schließen eine Taste drücken …"
read -k 1 