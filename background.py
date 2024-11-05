import pygame
import random

#TODO Zrobić tą zasraną kolizje z drzewami

# Constants
TILE_SIZE = 64
TREE_SIZE = 128
map_file = "map.txt"

def load_background_graphics():
    # Load and scale base tile graphics
    tile_image = pygame.image.load('Grafiki/Landscape/kafelek.png').convert_alpha()
    tile_image = pygame.transform.scale(tile_image, (TILE_SIZE, TILE_SIZE))

    # Load animated leaves
    leaves_animation = []
    for i in range(5):
        leaves_img = pygame.image.load(f'Grafiki/Landscape/Leaves/{i}.png').convert_alpha()
        leaves_img = pygame.transform.scale(leaves_img, (128, 128))
        leaves_animation.append(leaves_img)

    # Load and scale tree images to 128x128
    tree_images = []
    for i in range(1, 3):
        tree_img = pygame.image.load(f'Grafiki/Landscape/Tree{i}.png').convert_alpha()
        tree_img = pygame.transform.scale(tree_img, (TREE_SIZE, TREE_SIZE))
        tree_images.append(tree_img)

    # Load path image and scale it to 64x64
    path_image = pygame.image.load('Grafiki/Landscape/path.png').convert_alpha()
    path_image = pygame.transform.scale(path_image, (TILE_SIZE, TILE_SIZE))

    return tile_image, leaves_animation, tree_images, path_image

class Background:
    def __init__(self, map_width, map_height, tile_size, screen_width, screen_height):
        # Load all graphics
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
        self.tree_positions = self.generate_tree_positions()

    def load_map_from_file(self, map_file):
        map_data = []
        with open(map_file, 'r') as f:
            for line in f:
                row = []
                for symbol in line.strip():
                    tile_type = self.map_symbol_to_type(symbol)
                    row.append(tile_type)
                map_data.append(row)
        return map_data

    def map_symbol_to_type(self, symbol):
        if symbol == '0':
            return 'grass'
        elif symbol == '1':
            return 'path'
        return 'grass'

    def generate_tree_positions(self):
        tree_positions = []
        for y in range(len(self.map_data)):
            for x in range(len(self.map_data[y])):
                if self.map_data[y][x] == 'grass' and self.is_isolated_grass(x, y):
                    # Randomly select a tree image index
                    tree_image_index = random.choice(range(len(self.tree_images)))
                    tree_positions.append((x, y, tree_image_index))
        return tree_positions

    def is_isolated_grass(self, x, y):
        # Check neighboring tiles to ensure there are no paths
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                # Skip out-of-bounds neighbors
                if nx < 0 or ny < 0 or nx >= len(self.map_data[0]) or ny >= len(self.map_data):
                    continue
                # If any neighboring tile is a path, return False
                if self.map_data[ny][nx] == 'path':
                    return False
        return True

    def draw_base_map(self, screen, camera_offset):
        # Draw base map tiles (grass and path)
        for y, row in enumerate(self.map_data):
            for x, tile_type in enumerate(row):
                pos = (x * self.tile_size - camera_offset[0], y * self.tile_size - camera_offset[1])

                if tile_type == 'grass':
                    screen.blit(self.tile_image, pos)
                elif tile_type == 'path':
                    screen.blit(self.path_image, pos)

    def draw_trees(self, screen, camera_offset):
        # Draw trees as a separate layer
        for x, y, tree_image_index in self.tree_positions:
            # Calculate tree position so that it's centered within the tile grid
            tree_pos = (x * self.tile_size - camera_offset[0] - (TREE_SIZE - TILE_SIZE) // 2,
                        y * self.tile_size - camera_offset[1] - (TREE_SIZE - TILE_SIZE) // 2)
            tree_image = self.tree_images[tree_image_index]
            screen.blit(tree_image, tree_pos)

    def draw(self, screen, camera_offset, player):
        # Draw base map layer
        self.draw_base_map(screen, camera_offset)
        # Draw the player character here to ensure it appears "under" the trees
        player.draw(screen, camera_offset)

        # Draw trees as the topmost layer
        self.draw_trees(screen, camera_offset)

    def draw_leaves(self, screen, camera_offset):
        current_time = pygame.time.get_ticks()
        if current_time - self.l_timer > self.l_speed:
            self.l_frame = (self.l_frame + 1) % len(self.leaves_animation)
            self.l_timer = current_time

        for y in range(0, self.map_height * self.tile_size, self.leaves_size):
            for x in range(0, self.map_width * self.tile_size, self.leaves_size):
                pos = (x - camera_offset[0], y - camera_offset[1])
                screen.blit(self.leaves_animation[self.l_frame], pos)


