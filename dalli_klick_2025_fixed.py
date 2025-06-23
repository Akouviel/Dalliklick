#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dalli Klick 2025 - Ein Bildratespiel
Erstellt für die Hochzeit - Familienversion
Komplett tkinter-frei für macOS-Kompatibilität
"""

import pygame
import pygame_gui
import os
import random
import sys
from pathlib import Path

# Pygame initialisieren
pygame.init()

# Konstanten
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
BLUE = (0, 100, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_BLUE = (0, 70, 180)
DARK_GREEN = (0, 100, 0)

class DalliKlickGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dalli Klick 2025")
        self.clock = pygame.time.Clock()
        
        # pygame_gui Manager initialisieren
        self.manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Spielzustände
        self.state = "menu"  # menu, game, folder_select, settings, victory
        
        # Spielvariablen
        self.images = []
        self.current_image_index = 0
        self.current_image = None
        self.grid_size = 4  # Standard: 4x4
        self.tile_size = 0
        self.tiles = []
        self.revealed_tiles = set()
        self.selected_folder = ""
        
        # UI Elemente
        self.font_large = pygame.font.SysFont(['Inter', 'Helvetica', 'Arial'], 48)
        self.font_medium = pygame.font.SysFont(['Inter', 'Helvetica', 'Arial'], 36)
        self.font_small = pygame.font.SysFont(['Inter', 'Helvetica', 'Arial'], 24)
        
        # UI Buttons und Elemente
        self.buttons = {}
        # Standard-Ordner für Bilder
        self.default_folder = str(Path.home() / "Desktop" / "DK Fotos")
        self.create_ui_elements()
        
    def create_ui_elements(self):
        """UI Elemente erstellen"""
        # Hauptmenü Buttons
        button_width = 250
        button_height = 50
        start_y = 400
        
        # Start Button
        self.buttons['start'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((SCREEN_WIDTH - button_width) // 2, start_y, button_width, button_height),
            text='Spiel starten',
            manager=self.manager
        )
        
        # Einstellungen Button
        self.buttons['settings'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((SCREEN_WIDTH - button_width) // 2, start_y + 70, button_width, button_height),
            text='Einstellungen',
            manager=self.manager
        )
        
        # Beenden Button
        self.buttons['quit'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((SCREEN_WIDTH - button_width) // 2, start_y + 140, button_width, button_height),
            text='Beenden',
            manager=self.manager
        )
        
        # Einstellungen UI
        self.buttons['back'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(50, 50, 100, 40),
            text='Zurück',
            manager=self.manager
        )
        
        # Schwierigkeits-Buttons
        difficulties = [3, 4, 5, 6, 8]
        diff_button_width = 80
        diff_start_x = (SCREEN_WIDTH - len(difficulties) * (diff_button_width + 10)) // 2
        diff_y = 300
        
        for i, diff in enumerate(difficulties):
            self.buttons[f'diff_{diff}'] = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(diff_start_x + i * (diff_button_width + 10), diff_y, diff_button_width, 40),
                text=f'{diff}x{diff}',
                manager=self.manager
            )
        
        # Spiel-UI
        self.buttons['next'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(SCREEN_WIDTH - 150, 50, 120, 40),
            text='Nächstes Bild',
            manager=self.manager
        )
        
        self.buttons['menu'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(50, 50, 100, 40),
            text='Menü',
            manager=self.manager
        )
        
        # Ordner-Auswahl UI
        self.buttons['select_folder'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((SCREEN_WIDTH - button_width) // 2, 350, button_width, button_height),
            text='Ordner auswählen',
            manager=self.manager
        )
        
        self.buttons['use_default'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((SCREEN_WIDTH - button_width) // 2, 420, button_width, button_height),
            text='Standard-Ordner verwenden',
            manager=self.manager
        )
        
        # Ordner-Pfad Text
        self.folder_text = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(100, 500, SCREEN_WIDTH - 200, 30),
            text=f'Standard-Ordner: {self.default_folder}',
            manager=self.manager
        )
        
        # Alle Buttons zunächst verstecken
        self.hide_all_buttons()
        
    def hide_all_buttons(self):
        """Alle Buttons verstecken"""
        for button in self.buttons.values():
            button.hide()
        if hasattr(self, 'folder_text'):
            self.folder_text.hide()
    
    def show_menu_buttons(self):
        """Hauptmenü Buttons anzeigen"""
        self.hide_all_buttons()
        self.buttons['start'].show()
        self.buttons['settings'].show()
        self.buttons['quit'].show()
    
    def show_settings_buttons(self):
        """Einstellungen Buttons anzeigen"""
        self.hide_all_buttons()
        self.buttons['back'].show()
        for key in self.buttons:
            if key.startswith('diff_'):
                self.buttons[key].show()
    
    def show_folder_select_buttons(self):
        """Ordner-Auswahl Buttons anzeigen"""
        self.hide_all_buttons()
        self.buttons['select_folder'].show()
        self.buttons['use_default'].show()
        self.buttons['back'].show()
        self.folder_text.show()
    
    def show_game_buttons(self):
        """Spiel-Buttons anzeigen"""
        self.hide_all_buttons()
        self.buttons['next'].show()
        self.buttons['menu'].show()
    
    def select_folder_dialog(self):
        """Einfacher Ordner-Auswahl-Dialog"""
        # Für macOS verwenden wir einen einfachen Dialog
        # In einer echten Anwendung könnte man hier eine native Dialog-API verwenden
        # Für jetzt verwenden wir den Standard-Ordner
        return self.default_folder
    
    def load_images_from_folder(self, folder_path):
        """Bilder aus dem angegebenen Ordner laden"""
        self.images = []
        if not os.path.exists(folder_path):
            return False
            
        # Unterstützte Bildformate
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')
        
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(image_extensions):
                try:
                    image_path = os.path.join(folder_path, filename)
                    image = pygame.image.load(image_path)
                    self.images.append(image)
                except pygame.error as e:
                    print(f"Fehler beim Laden von {filename}: {e}")
        
        if self.images:
            print(f"{len(self.images)} Bilder erfolgreich geladen!")
            return True
        else:
            print("Keine Bilder im ausgewählten Ordner gefunden!")
            return False
    
    def start_game(self):
        """Spiel starten"""
        if not self.images:
            # Versuche Standard-Ordner zu laden
            if self.load_images_from_folder(self.default_folder):
                self.selected_folder = self.default_folder
            else:
                return False
            
        self.current_image_index = 0
        self.state = "game"
        self.load_current_image()
        self.show_game_buttons()
        return True
    
    def load_current_image(self):
        """Aktuelles Bild laden und für das Raster vorbereiten"""
        if self.current_image_index >= len(self.images):
            # Alle Bilder durchgespielt
            self.show_victory_screen()
            return
            
        # Bild laden und an Bildschirmgröße anpassen
        original_image = self.images[self.current_image_index]
        
        # Berechne verfügbaren Platz für das Bild (mit Abstand für UI)
        image_area_width = SCREEN_WIDTH - 100
        image_area_height = SCREEN_HEIGHT - 200
        
        # Skaliere das Bild, um in den verfügbaren Platz zu passen
        img_width, img_height = original_image.get_size()
        scale_x = image_area_width / img_width
        scale_y = image_area_height / img_height
        scale = min(scale_x, scale_y)
        
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        self.current_image = pygame.transform.scale(original_image, (new_width, new_height))
        
        # Raster erstellen
        self.create_grid()
    
    def create_grid(self):
        """Raster für das aktuelle Bild erstellen"""
        if not self.current_image:
            return
            
        img_width, img_height = self.current_image.get_size()
        
        # Zentriere das Bild
        self.image_x = (SCREEN_WIDTH - img_width) // 2
        self.image_y = (SCREEN_HEIGHT - img_height) // 2 - 50
        
        # Kachelgröße berechnen
        self.tile_size = min(img_width // self.grid_size, img_height // self.grid_size)
        
        # Raster erstellen
        self.tiles = []
        self.revealed_tiles = set()
        
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                tile_x = self.image_x + col * self.tile_size
                tile_y = self.image_y + row * self.tile_size
                
                # Bildausschnitt für diese Kachel
                tile_surface = pygame.Surface((self.tile_size, self.tile_size))
                tile_surface.blit(self.current_image, (0, 0), 
                                (col * self.tile_size, row * self.tile_size, 
                                 self.tile_size, self.tile_size))
                
                self.tiles.append({
                    'rect': pygame.Rect(tile_x, tile_y, self.tile_size, self.tile_size),
                    'surface': tile_surface,
                    'row': row,
                    'col': col
                })
    
    def handle_events(self):
        """Ereignisse verarbeiten"""
        time_delta = self.clock.tick(FPS)/1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "game":
                        self.state = "menu"
                        self.show_menu_buttons()
                    elif self.state == "settings":
                        self.state = "menu"
                        self.show_menu_buttons()
                    elif self.state == "folder_select":
                        self.state = "menu"
                        self.show_menu_buttons()
                    elif self.state == "victory":
                        self.state = "menu"
                        self.show_menu_buttons()
                        
                elif event.key == pygame.K_SPACE and self.state == "game":
                    self.next_image()
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.state == "game":  # Linksklick
                    self.handle_click(event.pos)
                    
            # pygame_gui Events
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.buttons['start']:
                        if self.start_game():
                            pass
                        else:
                            self.state = "folder_select"
                            self.show_folder_select_buttons()
                            
                    elif event.ui_element == self.buttons['settings']:
                        self.state = "settings"
                        self.show_settings_buttons()
                        
                    elif event.ui_element == self.buttons['quit']:
                        return False
                        
                    elif event.ui_element == self.buttons['back']:
                        self.state = "menu"
                        self.show_menu_buttons()
                        
                    elif event.ui_element == self.buttons['next']:
                        self.next_image()
                        
                    elif event.ui_element == self.buttons['menu']:
                        self.state = "menu"
                        self.show_menu_buttons()
                        
                    elif event.ui_element == self.buttons['select_folder']:
                        folder = self.select_folder_dialog()
                        if folder and self.load_images_from_folder(folder):
                            self.selected_folder = folder
                            self.start_game()
                            
                    elif event.ui_element == self.buttons['use_default']:
                        if self.load_images_from_folder(self.default_folder):
                            self.selected_folder = self.default_folder
                            self.start_game()
                            
                    # Schwierigkeits-Buttons
                    for key in self.buttons:
                        if key.startswith('diff_'):
                            if event.ui_element == self.buttons[key]:
                                self.grid_size = int(key.split('_')[1])
                                break
            
            self.manager.process_events(event)
        
        self.manager.update(time_delta)
        return True
    
    def handle_click(self, pos):
        """Mausklick auf Kachel verarbeiten"""
        for i, tile in enumerate(self.tiles):
            if tile['rect'].collidepoint(pos):
                if i not in self.revealed_tiles:
                    self.revealed_tiles.add(i)
                break
    
    def next_image(self):
        """Zum nächsten Bild wechseln"""
        self.current_image_index += 1
        if self.current_image_index < len(self.images):
            self.load_current_image()
        else:
            self.show_victory_screen()
    
    def show_victory_screen(self):
        """Siegesschirm anzeigen"""
        self.state = "victory"
        self.hide_all_buttons()
    
    def draw_menu(self):
        """Hauptmenü zeichnen"""
        self.screen.fill(WHITE)
        # Titel
        title = self.font_large.render("Dalli Klick 2025", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)

        # Spalten-Konfiguration
        col_centers = [SCREEN_WIDTH // 6, SCREEN_WIDTH // 2, 5 * SCREEN_WIDTH // 6]
        block_top = 320
        num_offset = 0
        text_offset = 50
        block_height = 100  # Höhe für Nummer + Text
        # Linke Spalte: 1 Bilderordner wählen
        left_num = self.font_large.render("1", True, DARK_GREEN)
        left_num_rect = left_num.get_rect(center=(col_centers[0], block_top + num_offset))
        self.screen.blit(left_num, left_num_rect)
        left_title = self.font_medium.render("Bilderordner wählen", True, DARK_GREEN)
        left_title_rect = left_title.get_rect(center=(col_centers[0], block_top + text_offset))
        self.screen.blit(left_title, left_title_rect)
        # Mittlere Spalte: 2 Reihenfolge bestimmen
        center_num = self.font_large.render("2", True, DARK_GREEN)
        center_num_rect = center_num.get_rect(center=(col_centers[1], block_top + num_offset))
        self.screen.blit(center_num, center_num_rect)
        center_title = self.font_medium.render("Reihenfolge bestimmen", True, DARK_GREEN)
        center_title_rect = center_title.get_rect(center=(col_centers[1], block_top + text_offset))
        self.screen.blit(center_title, center_title_rect)
        # Rechte Spalte: 3 Schwierigkeitsgrad
        right_num = self.font_large.render("3", True, DARK_GREEN)
        right_num_rect = right_num.get_rect(center=(col_centers[2], block_top + num_offset))
        self.screen.blit(right_num, right_num_rect)
        right_title = self.font_medium.render("Schwierigkeitsgrad", True, DARK_GREEN)
        right_title_rect = right_title.get_rect(center=(col_centers[2], block_top + text_offset))
        self.screen.blit(right_title, right_title_rect)

        # Anweisungen unter dem linken Block
        left_lines = [
            "Klicke auf Kacheln, um sie aufzudecken",
            "Drücke LEERTASTE für das nächste Bild"
        ]
        for i, line in enumerate(left_lines):
            text = self.font_small.render(line, True, BLACK)
            text_rect = text.get_rect(center=(col_centers[0], block_top + text_offset + 40 + i * 30))
            self.screen.blit(text, text_rect)

        # Einheitlicher Abstand zu den Buttons
        button_width = 250
        button_height = 50
        start_y = block_top + block_height + 80  # Abstand nach unten
        start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((SCREEN_WIDTH - button_width) // 2, start_y, button_width, button_height),
            text='Spiel starten',
            manager=self.manager
        )
        start_button.show()
    
    def draw_settings(self):
        """Einstellungen-Bildschirm zeichnen"""
        self.screen.fill(WHITE)
        
        # Titel
        title = self.font_large.render("Einstellungen", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Schwierigkeitsgrad
        difficulty_text = self.font_medium.render("Wähle die Schwierigkeit:", True, BLACK)
        difficulty_rect = difficulty_text.get_rect(center=(SCREEN_WIDTH // 2, 250))
        self.screen.blit(difficulty_text, difficulty_rect)
        
        # Aktuelle Schwierigkeit
        current_diff = self.font_medium.render(f"Aktuell: {self.grid_size}x{self.grid_size}", True, DARK_BLUE)
        current_rect = current_diff.get_rect(center=(SCREEN_WIDTH // 2, 380))
        self.screen.blit(current_diff, current_rect)
    
    def draw_folder_select(self):
        """Ordner-Auswahl-Bildschirm zeichnen"""
        self.screen.fill(WHITE)
        
        # Titel
        title = self.font_large.render("Bilder auswählen", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Anweisungen
        instructions = [
            "Wähle einen Ordner mit Bildern aus:",
            "",
            "Unterstützte Formate: JPG, PNG, BMP, GIF, WEBP",
            "",
            "Oder verwende den Standard-Ordner:"
        ]
        
        y_offset = 200
        for instruction in instructions:
            text = self.font_medium.render(instruction, True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 40
    
    def draw_game(self):
        """Spielbildschirm zeichnen"""
        self.screen.fill(WHITE)
        
        if not self.current_image:
            return
        
        # Hintergrund für das Bild
        background_rect = pygame.Rect(self.image_x - 10, self.image_y - 10, 
                                    self.current_image.get_width() + 20, 
                                    self.current_image.get_height() + 20)
        pygame.draw.rect(self.screen, LIGHT_GRAY, background_rect)
        
        # Kacheln zeichnen
        for i, tile in enumerate(self.tiles):
            if i in self.revealed_tiles:
                # Aufgedeckte Kachel - zeige Bildausschnitt
                self.screen.blit(tile['surface'], tile['rect'])
            else:
                # Verdeckte Kachel - zeige grauen Block
                pygame.draw.rect(self.screen, DARK_GRAY, tile['rect'])
                pygame.draw.rect(self.screen, BLACK, tile['rect'], 2)  # Rahmen
        
        # UI-Informationen
        info_text = f"Bild {self.current_image_index + 1} von {len(self.images)}"
        info_surface = self.font_medium.render(info_text, True, BLACK)
        self.screen.blit(info_surface, (20, 20))
        
        # Anweisungen
        instructions = [
            "Klicke auf Kacheln zum Aufdecken",
            "LEERTASTE: Nächstes Bild",
            "ESC: Zurück zum Menü"
        ]
        
        y_offset = 60
        for instruction in instructions:
            text = self.font_small.render(instruction, True, BLACK)
            self.screen.blit(text, (20, y_offset))
            y_offset += 25
    
    def draw_victory(self):
        """Siegesschirm zeichnen"""
        self.screen.fill(WHITE)
        
        # Glückwunsch-Text
        congrats_text = self.font_large.render("Glückwunsch!", True, GREEN)
        congrats_rect = congrats_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(congrats_text, congrats_rect)
        
        # Alle Bilder durchgespielt
        all_done_text = self.font_medium.render("Du hast alle Bilder durchgespielt!", True, BLACK)
        all_done_rect = all_done_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(all_done_text, all_done_rect)
        
        # Zurück zum Menü
        menu_text = self.font_medium.render("Drücke ESC für das Hauptmenü", True, BLACK)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, 500))
        self.screen.blit(menu_text, menu_rect)
    
    def run(self):
        """Hauptspielschleife"""
        running = True
        self.show_menu_buttons()
        
        while running:
            running = self.handle_events()
            
            # Bildschirm zeichnen
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "settings":
                self.draw_settings()
            elif self.state == "folder_select":
                self.draw_folder_select()
            elif self.state == "game":
                self.draw_game()
            elif self.state == "victory":
                self.draw_victory()
            
            # pygame_gui zeichnen
            self.manager.draw_ui(self.screen)
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = DalliKlickGame()
    game.run() 