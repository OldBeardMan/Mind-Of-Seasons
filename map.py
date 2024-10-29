import pygame

# TODO Zaprogramować generowanie mapy z drzewami i ścieżką (folder Grafiki/Landscape)
# TODO Zaprogramować generowanie się kotków (Grafiki/NPC) na mapie pomiędzy drzewami

# Funkcja do ładowania grafiki tła i liści
def load_background_graphics():
    tile_image = pygame.image.load('Grafiki/Landscape/kafelek.png').convert_alpha()
    tile_image = pygame.transform.scale(tile_image, (64, 64))
    
    leaves_animation = []
    for i in range(5):
        leaves_img = pygame.image.load(f'Grafiki/Landscape/Leaves/{i}.png').convert_alpha()
        leaves_img = pygame.transform.scale(leaves_img, (128, 128))
        leaves_animation.append(leaves_img)
    
    return tile_image, leaves_animation

# Klasa Tła
class Background:
    def __init__(self, screen_width, screen_height):
        self.tile_image, self.leaves_animation = load_background_graphics()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tile_size = 64
        self.leaves_size = 128
        self.l_frame = 0
        self.l_timer = 0
        self.l_speed = 200

    def draw_tiles(self, screen):
        for y in range(0, self.screen_height, self.tile_size):
            for x in range(0, self.screen_width, self.tile_size):
                screen.blit(self.tile_image, (x, y))
    
    def draw_leaves(self, screen):
        current_time = pygame.time.get_ticks()
        if current_time - self.l_timer > self.l_speed:
            self.l_frame = (self.l_frame + 1) % len(self.leaves_animation)
            self.l_timer = current_time

        for y in range(0, self.screen_height, self.leaves_size):
            for x in range(0, self.screen_width, self.leaves_size):
                screen.blit(self.leaves_animation[self.l_frame], (x, y))
