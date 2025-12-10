import pygame
import random

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

    # Load and scale cat images
    cat_images = []
    for i in [2, 3, 5]:  # Assuming Cat3.png and Cat5.png exist
        cat_img = pygame.image.load(f'Grafiki/NPC/Cat{i}.png').convert_alpha()
        cat_img = pygame.transform.scale(cat_img, (TREE_SIZE // 2, TREE_SIZE // 2))  # Scale cats to half tree size
        cat_images.append(cat_img)

    return tile_image, leaves_animation, tree_images, path_image, cat_images

class Background:
    def __init__(self, map_width, map_height, tile_size, screen_width, screen_height):
        # Load all graphics
        self.tile_image, self.leaves_animation, self.tree_images, self.path_image, self.cat_images = load_background_graphics()
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
        self.cat_positions = self.generate_cat_positions()  # Add cat positions
        self.tree_collision_rects = self.generate_tree_collision_rects()

    def generate_tree_collision_rects(self):
        """Generuje prostokąty kolizji dla pni drzew (dolna część drzewa)"""
        collision_rects = []
        trunk_width = 30  # Szerokość pnia
        trunk_height = 40  # Wysokość pnia

        for x, y, tree_image_index in self.tree_positions:
            # Pozycja drzewa na mapie (w pikselach)
            tree_x = x * self.tile_size - (TREE_SIZE - TILE_SIZE) // 2
            tree_y = y * self.tile_size - (TREE_SIZE - TILE_SIZE) // 2

            # Hitbox pnia - wycentrowany na dole drzewa
            trunk_x = tree_x + (TREE_SIZE - trunk_width) // 2
            trunk_y = tree_y + TREE_SIZE - trunk_height - 10  # 10px od dołu

            collision_rects.append(pygame.Rect(trunk_x, trunk_y, trunk_width, trunk_height))

        return collision_rects

    def check_tree_collision(self, player_rect):
        """Sprawdza czy gracz koliduje z jakimkolwiek pniem drzewa"""
        for tree_rect in self.tree_collision_rects:
            if player_rect.colliderect(tree_rect):
                return True
        return False

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
                    # Dodaj drzewo z rzadkością
                    if random.random() < 0.5:
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

    def draw_leaves(self, screen, camera_offset):
        current_time = pygame.time.get_ticks()
        if current_time - self.l_timer > self.l_speed:
            self.l_frame = (self.l_frame + 1) % len(self.leaves_animation)
            self.l_timer = current_time

        for y in range(0, self.map_height * self.tile_size, self.leaves_size):
            for x in range(0, self.map_width * self.tile_size, self.leaves_size):
                pos = (x - camera_offset[0], y - camera_offset[1])
                screen.blit(self.leaves_animation[self.l_frame], pos)

    def generate_cat_positions(self):
        cat_positions = []

        # Zbierz pozycje drzew jako set dla szybkiego sprawdzania
        tree_tiles = set((x, y) for x, y, _ in self.tree_positions)

        # Znajdź pozycje na trawie, które NIE mają drzew i są blisko ścieżki (dostępne)
        available_positions = []
        for y in range(len(self.map_data)):
            for x in range(len(self.map_data[y])):
                if self.map_data[y][x] == 'grass' and (x, y) not in tree_tiles:
                    # Sprawdź czy jest blisko ścieżki (w promieniu 2 kafelków)
                    near_path = False
                    for dy in range(-2, 3):
                        for dx in range(-2, 3):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < len(self.map_data[0]) and 0 <= ny < len(self.map_data):
                                if self.map_data[ny][nx] == 'path':
                                    near_path = True
                                    break
                        if near_path:
                            break
                    if near_path:
                        available_positions.append((x, y))

        # Randomly select three positions for cats
        selected_positions = random.sample(available_positions, k=min(3, len(available_positions)))

        for x, y in selected_positions:
            cat_image_index = random.choice(range(len(self.cat_images)))
            cat_positions.append((x, y, cat_image_index))

        return cat_positions

    def get_cat_rects(self):
        """Zwraca listę prostokątów kolizji dla kotków"""
        cat_rects = []
        cat_size = TREE_SIZE // 2  # Rozmiar kotka
        for x, y, cat_image_index in self.cat_positions:
            cat_x = x * self.tile_size - (TREE_SIZE // 4)
            cat_y = y * self.tile_size - (TREE_SIZE // 4)
            cat_rect = pygame.Rect(cat_x, cat_y, cat_size, cat_size)
            cat_rects.append((cat_rect, cat_image_index, (x, y)))
        return cat_rects

    def check_cat_proximity(self, player_rect):
        """Sprawdza czy gracz jest blisko jakiegoś kotka i zwraca jego indeks"""
        proximity_distance = 60  # Dystans do interakcji
        for i, (x, y, cat_image_index) in enumerate(self.cat_positions):
            cat_x = x * self.tile_size - (TREE_SIZE // 4) + (TREE_SIZE // 4)  # Środek kotka
            cat_y = y * self.tile_size - (TREE_SIZE // 4) + (TREE_SIZE // 4)

            # Sprawdź dystans od środka gracza do środka kotka
            player_center_x = player_rect.centerx
            player_center_y = player_rect.centery

            distance = ((cat_x - player_center_x) ** 2 + (cat_y - player_center_y) ** 2) ** 0.5
            if distance < proximity_distance:
                return i, cat_image_index
        return None, None

    def collect_cat(self, cat_index):
        """Usuwa kotka z mapy po zebraniu"""
        if 0 <= cat_index < len(self.cat_positions):
            collected_cat = self.cat_positions.pop(cat_index)
            return collected_cat
        return None



    def draw_cats(self, screen, camera_offset):
        # Draw cats on the map
        for x, y, cat_image_index in self.cat_positions:
            # Calculate cat position centered within the tile grid
            cat_pos = (x * self.tile_size - camera_offset[0] - (TREE_SIZE // 4),
                       y * self.tile_size - camera_offset[1] - (TREE_SIZE // 4))
            cat_image = self.cat_images[cat_image_index]
            screen.blit(cat_image, cat_pos)

    def draw(self, screen, camera_offset, player):
        # Draw base map layer
        self.draw_base_map(screen, camera_offset)
        # Draw the player character here to ensure it appears "under" the trees
        player.draw(screen, camera_offset)

        # Draw trees and cats as the topmost layer
        self.draw_trees(screen, camera_offset)
        self.draw_cats(screen, camera_offset)  # Draw cats on top of other layers

