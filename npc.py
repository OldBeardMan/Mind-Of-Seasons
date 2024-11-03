
# TODO Kolizja ze sprytkiem nie jest precyzyjna, kiedyś mozna to poprawić
import pygame

#ładowanie grafiki sprytka
def  load_sprytek():
    image_sprytek=pygame.image.load('Grafiki/NPC/Sprytek.png')
    image_sprytek=pygame.transform.scale(image_sprytek,(60,70))
    return image_sprytek

def load_chat_graphics():
    image_chat=pygame.image.load('Grafiki/UI/dialog.png').convert_alpha()
    image_chat=pygame.transform.scale(image_chat, (200, 200))
    return image_chat

class Npc:
    def __init__(self, screen_width, screen_height, x, y):
        self.image_sprytek = load_sprytek()
        self.chat_graphics = load_chat_graphics()
        self.sprytek_position = pygame.math.Vector2(x, y)
        self.sprytek_rect = self.image_sprytek.get_rect(center=(x, y))
        self.chat_graphics_rect = self.chat_graphics.get_rect()
        self.screen_width = screen_width
        self.screen_height = screen_height

    # Rysuj sprytka mając na uwadze camere offset
    def draw_sprytek(self, screen, camera_offset):
        # Calculate position relative to the camera (both are Vector2, so we can subtract directly)
        sprytek_screen_position = self.sprytek_position - pygame.math.Vector2(camera_offset)
        screen.blit(self.image_sprytek, sprytek_screen_position)

#wyswietlanie chatu jesli jestesmy blisko sprytka
    def draw_chat_graphics(self, screen, player, camera_offset):
        # Inflate proximity rect for checking player's proximity to Sprytek
        proximity_rect = self.sprytek_rect.inflate(50, 50)
        if proximity_rect.colliderect(player.player_rect):
            # Position the chat graphic relative to Sprytek
            chat_position = self.sprytek_position - pygame.math.Vector2(camera_offset)
            
            # Offset the chat graphic above Sprytek for better visibility
            chat_position.y -= 140  # Adjust as needed to control vertical offset
            
            # Draw the chat graphic at the calculated screen position
            screen.blit(self.chat_graphics, chat_position)