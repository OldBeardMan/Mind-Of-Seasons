import pygame
import random

TILE_SIZE = 64

#TODO Poprawić generowanie ścieżki
#TODO dodać inne drzewa do generacji i zrobić kolizję z nimi

# Funkcja do ładowania grafiki tła, liści, drzew i ścieżek
def load_background_graphics():
    tile_image = pygame.image.load('Grafiki/Landscape/kafelek.png').convert_alpha()
    tile_image = pygame.transform.scale(tile_image, (TILE_SIZE, TILE_SIZE))
    
    leaves_animation = []
    for i in range(5):
        leaves_img = pygame.image.load(f'Grafiki/Landscape/Leaves/{i}.png').convert_alpha()
        leaves_img = pygame.transform.scale(leaves_img, (128, 128))
        leaves_animation.append(leaves_img)
    
    tree_image = pygame.image.load('Grafiki/Landscape/Tree1.png').convert_alpha()
    tree_image = pygame.transform.scale(tree_image, (TILE_SIZE, TILE_SIZE))
    
    path_image = pygame.image.load('Grafiki/Landscape/path.png').convert_alpha()
    path_image = pygame.transform.scale(path_image, (TILE_SIZE, TILE_SIZE))
    
    return tile_image, leaves_animation, tree_image, path_image

# Klasa Tła
class Background:
    def __init__(self, map_width, map_height, tile_size, screen_width, screen_height):
        self.tile_image, self.leaves_animation, self.tree_image, self.path_image = load_background_graphics()
        self.map_width = map_width
        self.map_height = map_height
        self.tile_size = tile_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.leaves_size = 128  # rozmiar animacji liści
        self.l_frame = 0
        self.l_timer = 0
        self.l_speed = 200  # prędkość animacji w ms
        self.map_data = self.generate_map_data()

    def generate_map_data(self):
        map_data = [['grass' for _ in range(self.map_width)] for _ in range(self.map_height)]
        x, y = self.map_width // 2, self.map_height // 2
        path_length = 50
        for _ in range(path_length):
            map_data[y][x] = 'path'
            direction = random.choice(['up', 'down', 'left', 'right'])
            if direction == 'up' and y > 0:
                y -= 1
            elif direction == 'down' and y < self.map_height - 1:
                y += 1
            elif direction == 'left' and x > 0:
                x -= 1
            elif direction == 'right' and x < self.map_width - 1:
                x += 1

        for y in range(self.map_height):
            for x in range(self.map_width):
                if map_data[y][x] == 'grass' and random.random() < 0.1:
                    map_data[y][x] = 'tree'

        return map_data

    def draw(self, screen, camera_offset):
        for y, row in enumerate(self.map_data):
            for x, tile_type in enumerate(row):
                pos = (x * self.tile_size - camera_offset[0], y * self.tile_size - camera_offset[1])
                if tile_type == 'grass':
                    screen.blit(self.tile_image, pos)
                elif tile_type == 'tree':
                    screen.blit(self.tile_image, pos)
                    screen.blit(self.tree_image, pos)
                elif tile_type == 'path':
                    screen.blit(self.path_image, pos)

    def draw_leaves(self, screen, camera_offset):
        current_time = pygame.time.get_ticks()
        if current_time - self.l_timer > self.l_speed:
            self.l_frame = (self.l_frame + 1) % len(self.leaves_animation)
            self.l_timer = current_time

        for y in range(0, self.map_height * self.tile_size, self.leaves_size):
            for x in range(0, self.map_width * self.tile_size, self.leaves_size):
                pos = (x - camera_offset[0], y - camera_offset[1])
                screen.blit(self.leaves_animation[self.l_frame], pos)
