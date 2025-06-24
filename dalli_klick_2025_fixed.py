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
BUTTON_TEXT = (255, 255, 255)  # Weiß für Text auf Buttons

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
        self.image_titles = []  # Liste der Bildtitel (Dateinamen ohne Endung)
        self.solution_checked = False  # Ob die Lösung schon geprüft wurde
        self.solution_correct = False  # Ob die Lösung korrekt war
        self.last_solution = ""
        self.selected_difficulty = 3  # Standard: 3x3
        
        # UI Elemente
        self.font_large = pygame.font.SysFont(['Inter', 'Helvetica', 'Arial'], 48)
        self.font_medium = pygame.font.SysFont(['Inter', 'Helvetica', 'Arial'], 36)
        self.font_small = pygame.font.SysFont(['Inter', 'Helvetica', 'Arial'], 24)
        
        # UI Buttons und Elemente
        self.buttons = {}
        # Standard-Ordner für Bilder
        self.default_folder = str(Path.home() / "Desktop" / "DK Fotos")
        self.create_ui_elements()
        
        # UI Theme für Buttons setzen
        self.set_custom_theme()
        
        # --- Neue Button-Rects für das Menü (werden in draw_menu gesetzt) ---
        self.menu_btn_rects = {}
        self.menu_btn_pressed = None  # Für visuelles Feedback
        self.shuffle_mode = False
        
        # Buttons für den Spielmodus als Attribute anlegen
        button_w, button_h = 160, 44
        spacing = 40
        self.btn_menu_rect = pygame.Rect(spacing, spacing, button_w, button_h)
        self.btn_next_rect = pygame.Rect(SCREEN_WIDTH - button_w - spacing, spacing, button_w, button_h)
        self.btn_reveal_rect = None
        
    def create_ui_elements(self):
        """UI Elemente erstellen (nur noch für andere Screens, nicht für das Menü)"""
        # Entferne alle UIManager-Buttons für das Menü!
        # (Die grünen Menü-Buttons werden manuell gezeichnet und verwaltet)
        self.buttons = {}
        self.buttons['back'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(50, 50, 100, 40),
            text='Zurück',
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
        # Alle Buttons zunächst verstecken
        self.hide_all_buttons()
        
    def hide_all_buttons(self):
        # Entferne alle pygame_gui-Elemente (Buttons etc.) zuverlässig.
        # (Legacy code for pygame_gui removed)
        pass

    def show_menu_buttons(self):
        self.hide_all_buttons()

    def show_settings_buttons(self):
        self.hide_all_buttons()

    def show_folder_select_buttons(self):
        self.hide_all_buttons()

    def show_game_buttons(self):
        self.hide_all_buttons()
        self.solution_checked = False
        self.solution_correct = False
        self.last_solution = ""
    
    def select_folder_dialog(self):
        """Einfacher Ordner-Auswahl-Dialog"""
        # Für macOS verwenden wir einen einfachen Dialog
        # In einer echten Anwendung könnte man hier eine native Dialog-API verwenden
        # Für jetzt verwenden wir den Standard-Ordner
        return self.default_folder
    
    def load_images_from_folder(self, folder_path):
        """Bilder aus dem angegebenen Ordner laden"""
        self.images = []
        self.image_titles = []
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
                    self.image_titles.append(os.path.splitext(filename)[0])
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
        self.grid_size = self.selected_difficulty
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
                if self.state == "menu":
                    for key, rect in self.menu_btn_rects.items():
                        if rect and rect.collidepoint(event.pos):
                            self.menu_btn_pressed = key
                            break
                elif event.button == 1 and self.state == "game":
                    if self.btn_menu_rect.collidepoint(event.pos):
                        self.state = "menu"
                    elif self.btn_next_rect.collidepoint(event.pos):
                        self.next_image()
                    elif self.btn_reveal_rect and self.btn_reveal_rect.collidepoint(event.pos):
                        self.revealed_tiles = set(range(len(self.tiles)))
                    else:
                        self.handle_click(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.state == "menu" and self.menu_btn_pressed:
                    key = self.menu_btn_pressed
                    rect = self.menu_btn_rects.get(key)
                    if rect and rect.collidepoint(event.pos):
                        if key == 'start':
                            self.start_game()
                        elif key == 'settings':
                            self.state = "settings"
                            self.show_settings_buttons()
                        elif key == 'quit' or key == 'beenden':
                            pygame.quit()
                            sys.exit()
                        elif key == 'sort_name' or key == 'nach_name':
                            self.shuffle_mode = False
                        elif key == 'sort_shuffle' or key == 'zufaellig':
                            self.shuffle_mode = True
                        elif key == 'diff_small' or key == 'klein':
                            self.selected_difficulty = 3
                        elif key == 'diff_large' or key == 'gross':
                            self.selected_difficulty = 6
                    self.menu_btn_pressed = None
            # pygame_gui Events (nur noch für andere Screens, nicht für das Menü)
            if event.type == pygame.USEREVENT and self.state != "menu":
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if self.buttons.get('back') is not None and event.ui_element == self.buttons['back']:
                        self.state = "menu"
                        self.show_menu_buttons()
                    elif self.buttons.get('next') is not None and event.ui_element == self.buttons['next']:
                        self.next_image()
                    elif self.buttons.get('menu') is not None and event.ui_element == self.buttons['menu']:
                        self.state = "menu"
                        self.show_menu_buttons()
                    elif self.buttons.get('select_folder') is not None and event.ui_element == self.buttons['select_folder']:
                        folder = self.select_folder_dialog()
                        if folder and self.load_images_from_folder(folder):
                            self.selected_folder = folder
                            self.start_game()
                    elif self.buttons.get('use_default') is not None and event.ui_element == self.buttons['use_default']:
                        if self.load_images_from_folder(self.default_folder):
                            self.selected_folder = self.default_folder
                            self.start_game()
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
        self.hide_all_buttons()  # Vor jedem Neuzeichnen des Menüs alle alten UI-Elemente entfernen
        # 🧱 Block 1: Neue grüne Buttons als Dict (nur für das Menü)
        # Berechne zentrale Positionen wie gehabt
        block_width = 240
        block_spacing = 48
        total_width = 3 * block_width + 2 * block_spacing
        group_left = (SCREEN_WIDTH - total_width) // 2
        x2 = group_left + block_width + block_spacing
        center_x = x2 + block_width // 2
        button_w, button_h = 200, 50
        button_spacing = 30
        button_group_left = center_x - button_w // 2
        button_group_top = 204 + 220 + 60  # block_top + block_height + 60
        self.buttons = {
            'nach_name': {'rect': self.menu_btn_rects.get('sort_name'), 'text': 'Nach Name'},
            'zufaellig': {'rect': self.menu_btn_rects.get('sort_shuffle'), 'text': 'Zufällig'},
            'klein': {'rect': self.menu_btn_rects.get('diff_small'), 'text': 'Klein'},
            'gross': {'rect': self.menu_btn_rects.get('diff_large'), 'text': 'Groß'},
            'start': {'rect': pygame.Rect(button_group_left, button_group_top, button_w, button_h), 'text': 'Spiel starten'},
            'settings': {'rect': pygame.Rect(button_group_left, button_group_top + button_h + button_spacing, button_w, button_h), 'text': 'Einstellungen'},
            'beenden': {'rect': pygame.Rect(button_group_left, button_group_top + 2 * (button_h + button_spacing), button_w, button_h), 'text': 'Beenden'}
        }
        # 🧱 Block 4: Zusätzliche Absicherung – lösche alte Button-Einträge
        for key in list(self.buttons.keys()):
            if key not in ['nach_name', 'zufaellig', 'klein', 'gross', 'start', 'settings', 'beenden']:
                del self.buttons[key]
        self.screen.fill(WHITE)
        # Titel etwas nach unten verschoben
        title = self.font_large.render("Dalli Klick", True, DARK_GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120 + 24))
        self.screen.blit(title, title_rect)
        # Block-Layout-Parameter
        block_width = 240
        block_height = 220
        block_top = 204
        block_spacing = 48
        total_width = 3 * block_width + 2 * block_spacing
        group_left = (SCREEN_WIDTH - total_width) // 2
        block_num_font = pygame.font.SysFont(['Inter', 'Helvetica', 'Arial'], 32, bold=True)
        block_title_font = pygame.font.SysFont(['Inter', 'Helvetica', 'Arial'], 26, bold=True)
        block_label_font = pygame.font.SysFont(['Inter', 'Helvetica', 'Arial'], 18)
        def render_multiline_centered(text, font, color, center, line_height=30):
            lines = text.split('\n')
            total_height = len(lines) * line_height
            y_start = center[1] - total_height // 2 + line_height // 2
            for i, line in enumerate(lines):
                surf = font.render(line, True, color)
                rect = surf.get_rect(center=(center[0], y_start + i * line_height))
                self.screen.blit(surf, rect)
        # Block 1: Bilderordner wählen
        x1 = group_left
        y = block_top
        num1 = block_num_font.render("1", True, DARK_GREEN)
        num1_rect = num1.get_rect(center=(x1 + block_width // 2, y + 20))
        self.screen.blit(num1, num1_rect)
        # Überschrift (grün, zentriert)
        title_y = y + 60
        render_multiline_centered("Bilderordner\nwählen", block_title_font, DARK_GREEN, (x1 + block_width // 2, title_y))
        # Erklärtexte (klein, zentriert, Bulletpoints, Abstand)
        font_small = pygame.font.SysFont(None, 18)
        bullet_lines = [
            "– Klicke auf Kacheln, um sie aufzudecken",
            "– Drücke LEERTASTE für das nächste Bild"
        ]
        bullet_y_start = title_y + 40  # Abstand unter Überschrift
        for i, line in enumerate(bullet_lines):
            text = font_small.render(line, True, BLACK)
            text_rect = text.get_rect(center=(x1 + block_width // 2, bullet_y_start + i * 24))
            self.screen.blit(text, text_rect)
        # Ausreichend Abstand nach unten zu weiteren UI-Elementen bleibt erhalten
        # Block 2: Reihenfolge bestimmen
        x2 = x1 + block_width + block_spacing
        num2 = block_num_font.render("2", True, DARK_GREEN)
        num2_rect = num2.get_rect(center=(x2 + block_width // 2, y + 20))
        self.screen.blit(num2, num2_rect)
        render_multiline_centered("Reihenfolge\nbestimmen", block_title_font, DARK_GREEN, (x2 + block_width // 2, y + 60))
        btn_font = block_label_font
        btn_w, btn_h = 120, 36
        btn_y = y + 105
        btn1_rect = pygame.Rect(x2 + block_width // 2 - btn_w // 2, btn_y, btn_w, btn_h)
        btn2_rect = pygame.Rect(x2 + block_width // 2 - btn_w // 2, btn_y + btn_h + 10, btn_w, btn_h)
        self.menu_btn_rects['sort_name'] = btn1_rect
        self.menu_btn_rects['sort_shuffle'] = btn2_rect
        color_name = (43, 101, 75) if self.menu_btn_pressed == 'sort_name' else (45, 106, 79)
        color_shuffle = (43, 101, 75) if self.menu_btn_pressed == 'sort_shuffle' else (45, 106, 79)
        pygame.draw.rect(self.screen, color_name, btn1_rect, border_radius=8)
        btn1_text = btn_font.render("Nach Name", True, (255, 255, 255))
        btn1_text_rect = btn1_text.get_rect(center=btn1_rect.center)
        self.screen.blit(btn1_text, btn1_text_rect)
        pygame.draw.rect(self.screen, color_shuffle, btn2_rect, border_radius=8)
        btn2_text = btn_font.render("Zufällig", True, (255, 255, 255))
        btn2_text_rect = btn2_text.get_rect(center=btn2_rect.center)
        self.screen.blit(btn2_text, btn2_text_rect)
        # Block 3: Schwierigkeitsgrad
        x3 = x2 + block_width + block_spacing
        num3 = block_num_font.render("3", True, DARK_GREEN)
        num3_rect = num3.get_rect(center=(x3 + block_width // 2, y + 20))
        self.screen.blit(num3, num3_rect)
        render_multiline_centered("Schwierigkeits-\ngrad", block_title_font, DARK_GREEN, (x3 + block_width // 2, y + 60))
        btn3_w, btn3_h = 100, 36
        btn3_y = y + 105
        btn_small_rect = pygame.Rect(x3 + block_width // 2 - btn3_w // 2, btn3_y, btn3_w, btn3_h)
        btn_large_rect = pygame.Rect(x3 + block_width // 2 - btn3_w // 2, btn3_y + btn3_h + 10, btn3_w, btn3_h)
        self.menu_btn_rects['diff_small'] = btn_small_rect
        self.menu_btn_rects['diff_large'] = btn_large_rect
        color_small = (43, 101, 75) if self.menu_btn_pressed == 'diff_small' else (45, 106, 79) if self.selected_difficulty == 3 else (255, 255, 255)
        color_large = (43, 101, 75) if self.menu_btn_pressed == 'diff_large' else (45, 106, 79) if self.selected_difficulty == 6 else (255, 255, 255)
        border_small = 3 if self.selected_difficulty == 3 else 2
        border_large = 3 if self.selected_difficulty == 6 else 2
        pygame.draw.rect(self.screen, color_small, btn_small_rect, border_radius=8)
        pygame.draw.rect(self.screen, (45, 106, 79), btn_small_rect, border_small, border_radius=8)
        text_col_small = (255, 255, 255) if self.selected_difficulty == 3 else (45, 106, 79)
        text_small = btn_font.render("Klein", True, text_col_small)
        text_small_rect = text_small.get_rect(center=btn_small_rect.center)
        self.screen.blit(text_small, text_small_rect)
        pygame.draw.rect(self.screen, color_large, btn_large_rect, border_radius=8)
        pygame.draw.rect(self.screen, (45, 106, 79), btn_large_rect, border_large, border_radius=8)
        text_col_large = (255, 255, 255) if self.selected_difficulty == 6 else (45, 106, 79)
        text_large = btn_font.render("Groß", True, text_col_large)
        text_large_rect = text_large.get_rect(center=btn_large_rect.center)
        self.screen.blit(text_large, text_large_rect)
        # --- Neue zentrale Button-Gruppe unter Spalte 2 ---
        button_w, button_h = 200, 50
        button_spacing = 30
        block_width = 240
        block_spacing = 48
        total_width = 3 * block_width + 2 * block_spacing
        group_left = (SCREEN_WIDTH - total_width) // 2
        x2 = group_left + block_width + block_spacing
        center_x = x2 + block_width // 2
        button_group_left = center_x - button_w // 2
        button_group_top = block_top + block_height + 60
        btn_start_rect = pygame.Rect(button_group_left, button_group_top, button_w, button_h)
        btn_settings_rect = pygame.Rect(button_group_left, button_group_top + button_h + button_spacing, button_w, button_h)
        btn_quit_rect = pygame.Rect(button_group_left, button_group_top + 2 * (button_h + button_spacing), button_w, button_h)
        self.menu_btn_rects['start'] = btn_start_rect
        self.menu_btn_rects['settings'] = btn_settings_rect
        self.menu_btn_rects['quit'] = btn_quit_rect
        BUTTON_GREEN = (26, 112, 49)
        BUTTON_GREEN_DARK = (24, 106, 46)
        BUTTON_TEXT_FONT = pygame.font.SysFont(['Inter', 'Helvetica', 'Arial'], 20, bold=True)
        BUTTON_RADIUS = 10
        color_start = BUTTON_GREEN_DARK if self.menu_btn_pressed == 'start' else BUTTON_GREEN
        color_settings = BUTTON_GREEN_DARK if self.menu_btn_pressed == 'settings' else BUTTON_GREEN
        color_quit = BUTTON_GREEN_DARK if self.menu_btn_pressed == 'quit' else BUTTON_GREEN
        pygame.draw.rect(self.screen, color_start, btn_start_rect, border_radius=BUTTON_RADIUS)
        btn_start_text = BUTTON_TEXT_FONT.render("Spiel starten", True, BUTTON_TEXT)
        btn_start_text_rect = btn_start_text.get_rect(center=btn_start_rect.center)
        self.screen.blit(btn_start_text, btn_start_text_rect)
        pygame.draw.rect(self.screen, color_settings, btn_settings_rect, border_radius=BUTTON_RADIUS)
        btn_settings_text = BUTTON_TEXT_FONT.render("Einstellungen", True, BUTTON_TEXT)
        btn_settings_text_rect = btn_settings_text.get_rect(center=btn_settings_rect.center)
        self.screen.blit(btn_settings_text, btn_settings_text_rect)
        pygame.draw.rect(self.screen, color_quit, btn_quit_rect, border_radius=BUTTON_RADIUS)
        btn_quit_text = BUTTON_TEXT_FONT.render("Beenden", True, BUTTON_TEXT)
        btn_quit_text_rect = btn_quit_text.get_rect(center=btn_quit_rect.center)
        self.screen.blit(btn_quit_text, btn_quit_text_rect)
    
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
                self.screen.blit(tile['surface'], tile['rect'])
            else:
                pygame.draw.rect(self.screen, DARK_GRAY, tile['rect'])
                pygame.draw.rect(self.screen, BLACK, tile['rect'], 2)
        # Entferne alte graue Menü- und Nächstes-Bild-Buttons (keine draw.rect/screen.blit mehr für diese)
        # Die neuen runden Buttons werden von pygame_gui oder eigener Klasse gezeichnet
        # Bild aufdecken-Button bleibt wie gehabt
        button_w, button_h = 200, 50
        reveal_x = (SCREEN_WIDTH - button_w) // 2
        reveal_y = self.image_y + self.current_image.get_height() + 40
        self.btn_reveal_rect = pygame.Rect(reveal_x, reveal_y, button_w, button_h)
        pygame.draw.rect(self.screen, DARK_GRAY, self.btn_reveal_rect, border_radius=8)
        font = pygame.font.SysFont(['Inter', 'Helvetica', 'Arial'], 28)
        reveal_text = font.render("Bild aufdecken", True, (255, 255, 255))
        reveal_text_rect = reveal_text.get_rect(center=self.btn_reveal_rect.center)
        self.screen.blit(reveal_text, reveal_text_rect)
    
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
    
    def set_custom_theme(self):
        # Erstelle ein Theme mit grünem Button-Hintergrund, weißer Schrift und abgerundeten Ecken
        theme_string = '''{
            "button": {
                "colours": {
                    "normal_bg": "#218c3a",
                    "hovered_bg": "#27ae60",
                    "disabled_bg": "#b2b2b2",
                    "active_bg": "#145a24",
                    "normal_text": "#ffffff",
                    "hovered_text": "#ffffff",
                    "active_text": "#ffffff",
                    "disabled_text": "#f0f0f0"
                },
                "shape": "rounded_rectangle",
                "border_width": 0,
                "shadow_width": 0,
                "border_radius": 12
            }
        }'''
        import io
        self.manager.get_theme().load_theme(io.StringIO(theme_string))
    
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