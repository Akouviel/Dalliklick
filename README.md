# Dalli Klick 2025

Ein Bildratespiel in Python mit Pygame, inspiriert von "Dalli Klick".

## Installation

### Voraussetzungen
- Python 3.7 oder höher
- macOS (getestet auf älteren Macs)

### Installation der Abhängigkeiten

1. Öffne das Terminal
2. Navigiere zu deinem Projektordner:
   ```bash
   cd /Users/akouvimasseme/Desktop
   ```

3. Installiere die benötigten Pakete:
   ```bash
   pip3 install -r requirements.txt
   ```

   Falls pip3 nicht funktioniert, versuche:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

## Spiel starten

```bash
python3 dalli_klick_2025.py
```

## Spielanleitung

### Hauptmenü
- **Ordner auswählen**: Wähle einen Ordner mit Bildern von deiner Festplatte
- **Schwierigkeit**: Ändere die Anzahl der Kacheln (3x3 bis 8x8)

### Spielablauf
1. Nach der Ordnerauswahl wird das erste Bild geladen
2. Das Bild wird in Kacheln aufgeteilt und verdeckt angezeigt
3. **Klicke** mit der Maus auf Kacheln, um sie aufzudecken
4. **LEERTASTE** für das nächste Bild
5. **ESC** für das Hauptmenü

### Unterstützte Bildformate
- JPG/JPEG
- PNG
- BMP
- GIF
- WebP

## Tipps für die Hochzeit

- Erstelle einen Ordner mit Fotos der Brautleute, Familie und Freunden
- Verwende Bilder mit guter Qualität (mindestens 800x600 Pixel)
- Teste das Spiel vorher mit einigen Bildern
- Stelle sicher, dass alle Bilder im gleichen Ordner sind

## Fehlerbehebung

### "pygame module not found"
```bash
pip3 install pygame
```

### "tkinter not available"
Tkinter ist normalerweise bereits mit Python installiert. Falls nicht:
```bash
brew install python-tk
```

### Bilder werden nicht geladen
- Überprüfe, ob die Bilder in unterstützten Formaten sind
- Stelle sicher, dass der Ordnerpfad korrekt ist
- Teste mit einem einfachen Ordner ohne Sonderzeichen im Namen

## Projektstruktur

```
Desktop/
├── dalli_klick_2025.py    # Hauptspieldatei
├── requirements.txt       # Python-Abhängigkeiten
├── README.md             # Diese Anleitung
└── DK Fotos/             # Dein Bildordner (optional)
```

Viel Spaß beim Spielen! 🎮📸 