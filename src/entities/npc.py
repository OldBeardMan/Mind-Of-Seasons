
# TODO Kolizja ze sprytkiem nie jest precyzyjna, kiedyś mozna to poprawić
import pygame

#ładowanie grafiki sprytka
def load_sprytek():
    image_sprytek=pygame.image.load('Grafiki/NPC/Sprytek.png')
    image_sprytek=pygame.transform.scale(image_sprytek,(60,70))
    return image_sprytek

def load_chat_graphics():
    image_chat=pygame.image.load('Grafiki/UI/dialog.png').convert_alpha()
    image_chat=pygame.transform.scale(image_chat, (350, 200))
    return image_chat

# Sprytek Dialogs
SPRYTEK_DIALOGS = [
    {
        "id": "greeting",
        "texts": [
            "Hello! I am Sprytek!",
            "I will help you collect cats.",
            "Press F to talk to me!"
        ]
    },
    {
        "id": "quest_intro",
        "texts": [
            "I have a quest for you!",
            "Many cats got lost in this area.",
            "Could you find and collect them?",
            "Just walk to a cat and press F!"
        ]
    },
    {
        "id": "encouragement",
        "texts": [
            "You are doing great!",
            "Keep searching for cats!"
        ]
    },
    {
        "id": "random_1",
        "texts": [
            "You know, cats like to hide behind trees.",
            "Look around carefully!"
        ]
    },
    {
        "id": "random_2",
        "texts": [
            "Beautiful weather for a walk, right?",
            "Perfect for finding cats!"
        ]
    }
]

class Npc:
    def __init__(self, screen_width, screen_height, x, y):
        self.image_sprytek = load_sprytek()
        self.chat_graphics = load_chat_graphics()
        self.sprytek_position = pygame.math.Vector2(x, y)
        self.sprytek_rect = self.image_sprytek.get_rect(center=(x, y))
        self.chat_graphics_rect = self.chat_graphics.get_rect()
        self.screen_width = screen_width
        self.screen_height = screen_height

        # System dialogu
        self.is_talking = False
        self.current_dialog_index = 0
        self.current_text_index = 0
        self.dialog_cooldown = 0
        self.player_near = False
        self.f_key_pressed = False

        # Font do tekstu dialogu (pixelowy)
        pygame.font.init()
        self.dialog_font = pygame.font.Font('Czcionki/PressStart2P.ttf', 10)

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
            # Position the chat graphic relative to Sprytek
            chat_position = self.sprytek_position - pygame.math.Vector2(camera_offset)

            # Offset the chat graphic to the right of Sprytek
            chat_position.y -= 120
            chat_position.x += 40  # Dymek na prawo od Sprytka

            # Draw the chat graphic at the calculated screen position
            screen.blit(self.chat_graphics, chat_position)

            # Wyświetl tekst dialogu lub podpowiedź
            if self.is_talking:
                current_dialog = SPRYTEK_DIALOGS[self.current_dialog_index]
                current_text = current_dialog["texts"][self.current_text_index]
                self._draw_dialog_text(screen, current_text, chat_position)
            else:
                # Hint that player can press F
                hint_text = "[F] Talk"
                self._draw_dialog_text(screen, hint_text, chat_position)

    def _draw_dialog_text(self, screen, text, chat_position):
        # Pozycja tekstu wewnątrz dymku
        text_x = chat_position.x + 90
        text_y = chat_position.y + 60
        max_width = 220

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

        # Rysowanie linii tekstu
        for i, line in enumerate(lines):
            text_surface = self.dialog_font.render(line, True, (50, 50, 50))
            screen.blit(text_surface, (text_x, text_y + i * 16))

        # Continue hint (if there is more text)
        if self.is_talking:
            current_dialog = SPRYTEK_DIALOGS[self.current_dialog_index]
            if self.current_text_index < len(current_dialog["texts"]) - 1:
                continue_text = "[F] Next..."
            else:
                continue_text = "[F] End"
            continue_surface = self.dialog_font.render(continue_text, True, (100, 100, 100))
            screen.blit(continue_surface, (text_x, text_y + len(lines) * 16 + 10))