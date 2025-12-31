
# TODO Collision with Sprytek is not precise, can be improved later
import json
import pygame
from src.utils import get_image, get_font, resource_path


# Load Sprytek graphics (uses cache)
def load_sprytek():
    return get_image('graphics/npc/sprytek.png', (60, 70))


def _load_dialogs():
    """Load Sprytek dialogs from JSON file."""
    with open(resource_path('data/dialogs.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('sprytek', [])


# Load dialogs from JSON
SPRYTEK_DIALOGS = _load_dialogs()

class Npc:
    def __init__(self, screen_width, screen_height, x, y):
        self.image_sprytek = load_sprytek()
        self.sprytek_position = pygame.math.Vector2(x, y)
        self.sprytek_rect = self.image_sprytek.get_rect(center=(x, y))
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Rozmiary dymku dialogowego
        self.bubble_width = 320
        self.bubble_height = 140
        self.bubble_padding = 15
        self.bubble_color = (45, 40, 35)
        self.bubble_border_color = (180, 160, 120)

        # System dialogu
        self.is_talking = False
        self.current_dialog_index = 0
        self.current_text_index = 0
        self.dialog_cooldown = 0
        self.player_near = False
        self.f_key_pressed = False

        # Font do tekstu dialogu (pixelowy) - uses cache
        self.dialog_font = get_font(10)
        self.hint_font = get_font(8)

    # Rysuj sprytka mając na uwadze camere offset
    def draw_sprytek(self, screen, camera_offset):
        # Calculate position relative to the camera (both are Vector2, so we can subtract directly)
        sprytek_screen_position = self.sprytek_position - pygame.math.Vector2(camera_offset)
        screen.blit(self.image_sprytek, sprytek_screen_position)

    def update(self, keys, player):
        # Sprawdź bliskość gracza
        proximity_rect = self.sprytek_rect.inflate(50, 50)
        self.player_near = proximity_rect.colliderect(player.player_rect)

        # Obsługa cooldownu
        if self.dialog_cooldown > 0:
            self.dialog_cooldown -= 1

        # Obsługa klawisza F
        if keys[pygame.K_f] and not self.f_key_pressed and self.dialog_cooldown == 0:
            self.f_key_pressed = True
            if self.player_near:
                if not self.is_talking:
                    # Rozpocznij rozmowę
                    self.is_talking = True
                    self.current_text_index = 0
                else:
                    # Przejdź do następnego tekstu
                    self.current_text_index += 1
                    current_dialog = SPRYTEK_DIALOGS[self.current_dialog_index]
                    if self.current_text_index >= len(current_dialog["texts"]):
                        # Zakończ ten dialog, przejdź do następnego
                        self.is_talking = False
                        self.current_text_index = 0
                        self.current_dialog_index = (self.current_dialog_index + 1) % len(SPRYTEK_DIALOGS)
                self.dialog_cooldown = 15  # Krótki cooldown między naciśnięciami

        if not keys[pygame.K_f]:
            self.f_key_pressed = False

        # Jeśli gracz odejdzie podczas rozmowy, zakończ ją
        if not self.player_near and self.is_talking:
            self.is_talking = False
            self.current_text_index = 0

    def draw_chat_graphics(self, screen, player, camera_offset):
        # Inflate proximity rect for checking player's proximity to Sprytek
        proximity_rect = self.sprytek_rect.inflate(50, 50)
        if proximity_rect.colliderect(player.player_rect):
            # Pozycja Sprytka na ekranie
            sprytek_screen = self.sprytek_position - pygame.math.Vector2(camera_offset)

            # Pozycja dymku - nad Sprytkiem, lekko na prawo
            bubble_x = sprytek_screen.x + 30
            bubble_y = sprytek_screen.y - self.bubble_height - 20

            # Rysuj dymek
            self._draw_speech_bubble(screen, bubble_x, bubble_y, sprytek_screen)

            # Wyświetl tekst dialogu lub podpowiedź
            if self.is_talking:
                current_dialog = SPRYTEK_DIALOGS[self.current_dialog_index]
                current_text = current_dialog["texts"][self.current_text_index]
                self._draw_dialog_text(screen, current_text, bubble_x, bubble_y)
            else:
                # Hint that player can press F
                hint_text = "[F] Talk"
                self._draw_dialog_text(screen, hint_text, bubble_x, bubble_y)

    def _draw_speech_bubble(self, screen, x, y, sprytek_pos):
        """Rysuje prostokątny dymek dialogowy ze strzałką"""
        # Główny prostokąt dymku
        bubble_rect = pygame.Rect(x, y, self.bubble_width, self.bubble_height)

        # Rysuj tło dymku z zaokrąglonymi rogami
        pygame.draw.rect(screen, self.bubble_color, bubble_rect, border_radius=10)

        # Rysuj obramowanie
        pygame.draw.rect(screen, self.bubble_border_color, bubble_rect, 3, border_radius=10)

        # Strzałka wskazująca na Sprytka (trójkąt)
        arrow_size = 15
        arrow_points = [
            (x + 10, y + self.bubble_height),  # Lewy górny punkt strzałki
            (x + 10 + arrow_size, y + self.bubble_height),  # Prawy górny punkt
            (x - 5, y + self.bubble_height + arrow_size + 5)  # Dolny punkt (wskazuje na Sprytka)
        ]
        pygame.draw.polygon(screen, self.bubble_color, arrow_points)
        # Obramowanie strzałki (tylko zewnętrzne krawędzie)
        pygame.draw.line(screen, self.bubble_border_color, arrow_points[0], arrow_points[2], 3)
        pygame.draw.line(screen, self.bubble_border_color, arrow_points[1], arrow_points[2], 3)

    def _draw_dialog_text(self, screen, text, bubble_x, bubble_y):
        # Pozycja tekstu wewnątrz dymku
        text_x = bubble_x + self.bubble_padding
        text_y = bubble_y + self.bubble_padding
        max_width = self.bubble_width - (self.bubble_padding * 2)
        line_height = 16

        # Łamanie tekstu na linie
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            test_surface = self.dialog_font.render(test_line, True, (0, 0, 0))
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())

        # Rysowanie linii tekstu (jasny kolor na ciemnym tle)
        text_color = (230, 220, 200)
        for i, line in enumerate(lines):
            text_surface = self.dialog_font.render(line, True, text_color)
            screen.blit(text_surface, (text_x, text_y + i * line_height))

        # Continue hint (if there is more text) - na dole dymku
        if self.is_talking:
            current_dialog = SPRYTEK_DIALOGS[self.current_dialog_index]
            if self.current_text_index < len(current_dialog["texts"]) - 1:
                continue_text = "[F] Next..."
            else:
                continue_text = "[F] End"
            continue_surface = self.hint_font.render(continue_text, True, (150, 140, 120))
            # Stała pozycja na dole dymku
            hint_y = bubble_y + self.bubble_height - self.bubble_padding - 10
            screen.blit(continue_surface, (text_x, hint_y))