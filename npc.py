
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
    def __init__(self,screen_width,screen_height):
        self.image_sprytek = load_sprytek()
        self.sprytek_rect = self.image_sprytek.get_rect(center=(screen_width // 3, screen_height // 3))
        self.chat_graphics = load_chat_graphics()
        self.chat_graphics_rect = self.chat_graphics.get_rect(center=(screen_width // 2.7, screen_height // 3.7))
        self.screen_width = screen_width
        self.screen_height = screen_height



    def draw_sprytek(self, screen):
        screen.blit(self.image_sprytek, self.sprytek_rect)

#wyswietlanie chatu jesli jestesmy blisko sprytka
    def draw_chat_graphics(self, screen, player):
        proximity_rect = self.sprytek_rect.inflate(50,50) #inflate zwiększa obszar kolizji
        if proximity_rect.colliderect(player.player_rect):
            screen.blit(self.chat_graphics, self.chat_graphics_rect)