import pygame
import random

#TODO Przygotować plik map.txt z mapą

TILE_SIZE = 64
map_file = "map.txt"

def load_background_graphics():
    tile_image = pygame.image.load('Grafiki/Landscape/kafelek.png').convert_alpha()
    tile_image = pygame.transform.scale(tile_image, (TILE_SIZE, TILE_SIZE))

    leaves_animation = []
    for i in range(5):
        leaves_img = pygame.image.load(f'Grafiki/Landscape/Leaves/{i}.png').convert_alpha()
        leaves_img = pygame.transform.scale(leaves_img, (128, 128))
        leaves_animation.append(leaves_img)

    tree_images = []
    for i in range(1, 6):
        tree_img = pygame.image.load(f'Grafiki/Landscape/Tree{i}.png').convert_alpha()
        tree_img = pygame.transform.scale(tree_img, (TILE_SIZE, TILE_SIZE))
        tree_images.append(tree_img)

    path_image = pygame.image.load('Grafiki/Landscape/path.png').convert_alpha()
    path_image = pygame.transform.scale(path_image, (TILE_SIZE, TILE_SIZE))

    return tile_image, leaves_animation, tree_images, path_image

class Background:
    def __init__(self, map_width, map_height, tile_size, screen_width, screen_height):
        self.tile_image, self.leaves_animation, self.tree_images, self.path_image = load_background_graphics()
        self.map_width = map_width
        self.map_height = map_height
        self.tile_size = tile_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.leaves_size = 128
        self.l_frame = 0
        self.l_timer = 0
        self.l_speed = 200
        self.map_data = self.load_map_from_file(map_file)

    def load_map_from_file(self, map_file):
        map_data = []
        with open(map_file, 'r') as f:
            for line in f:
                row = []
                for symbol in line.strip():
                    tile_type = self.map_symbol_to_type(symbol)
                    if tile_type == 'tree':
                        # Losuj drzewo, jeśli symbol to drzewo
                        tree_image_index = random.choice(range(len(self.tree_images)))
                        row.append((tile_type, tree_image_index))
                    else:
                        row.append((tile_type, None))  # Brak drzewa
                map_data.append(row)
        return map_data

    def map_symbol_to_type(self, symbol):
        if symbol == '0':
            return 'grass'
        elif symbol == '1':
            return 'path'
        elif symbol in '2':
            return 'tree'
        return 'grass'

    def draw(self, screen, camera_offset):
        for y, row in enumerate(self.map_data):
            for x, (tile_type, tree_image_index) in enumerate(row):
                pos = (x * self.tile_size - camera_offset[0], y * self.tile_size - camera_offset[1])
                if tile_type == 'grass':
                    screen.blit(self.tile_image, pos)
                elif tile_type == 'tree' and tree_image_index is not None:
                    screen.blit(self.tile_image, pos)
                    # Rysuj konkretne drzewo wybrane podczas generacji mapy
                    tree_image = self.tree_images[tree_image_index]
                    screen.blit(tree_image, pos)
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
