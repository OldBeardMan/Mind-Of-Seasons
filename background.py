import pygame
import random

# Constants
TILE_SIZE = 64
TREE_SIZE = 128
MAP_FILE = "map.txt"


def load_graphics():
    """Load and scale all background graphics."""
    # Base tile
    tile_image = pygame.image.load('Grafiki/Landscape/kafelek.png').convert_alpha()
    tile_image = pygame.transform.scale(tile_image, (TILE_SIZE, TILE_SIZE))

    # Animated leaves
    leaves_animation = []
    for i in range(5):
        leaves_img = pygame.image.load(f'Grafiki/Landscape/Leaves/{i}.png').convert_alpha()
        leaves_img = pygame.transform.scale(leaves_img, (128, 128))
        leaves_animation.append(leaves_img)

    # Trees
    tree_images = []
    for i in range(1, 3):
        tree_img = pygame.image.load(f'Grafiki/Landscape/Tree{i}.png').convert_alpha()
        tree_img = pygame.transform.scale(tree_img, (TREE_SIZE, TREE_SIZE))
        tree_images.append(tree_img)

    # Path
    path_image = pygame.image.load('Grafiki/Landscape/path.png').convert_alpha()
    path_image = pygame.transform.scale(path_image, (TILE_SIZE, TILE_SIZE))

    # Cats
    cat_images = []
    for i in [2, 3, 5]:
        cat_img = pygame.image.load(f'Grafiki/NPC/Cat{i}.png').convert_alpha()
        cat_img = pygame.transform.scale(cat_img, (TREE_SIZE // 2, TREE_SIZE // 2))
        cat_images.append(cat_img)

    return tile_image, leaves_animation, tree_images, path_image, cat_images


class Background:
    def __init__(self, map_width, map_height, tile_size, screen_width, screen_height, cat_positions=None):
        self.tile_image, self.leaves_animation, self.tree_images, self.path_image, self.cat_images = load_graphics()
        self.map_width = map_width
        self.map_height = map_height
        self.tile_size = tile_size
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Leaves animation
        self.leaves_size = 128
        self.leaves_frame = 0
        self.leaves_timer = 0
        self.leaves_speed = 200

        # Load map and generate elements
        self.map_data = self._load_map(MAP_FILE)
        self.tree_positions = self._generate_trees()
        self.cat_positions = self._setup_cats(cat_positions) if cat_positions else self._generate_cats()
        self.tree_collision_rects = self._generate_tree_collisions()

    def _load_map(self, filename):
        """Load map from file."""
        map_data = []
        with open(filename, 'r') as f:
            for line in f:
                row = ['path' if c == '1' else 'grass' for c in line.strip()]
                map_data.append(row)
        return map_data

    def _is_isolated_grass(self, x, y):
        """Check if grass tile has no adjacent paths."""
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(self.map_data[0]) and 0 <= ny < len(self.map_data):
                    if self.map_data[ny][nx] == 'path':
                        return False
        return True

    def _generate_trees(self):
        """Generate tree positions on isolated grass tiles."""
        trees = []
        for y in range(len(self.map_data)):
            for x in range(len(self.map_data[y])):
                if self.map_data[y][x] == 'grass' and self._is_isolated_grass(x, y):
                    if random.random() < 0.5:
                        tree_idx = random.randrange(len(self.tree_images))
                        trees.append((x, y, tree_idx))
        return trees

    def _generate_tree_collisions(self):
        """Generate collision rectangles for tree trunks."""
        rects = []
        trunk_width, trunk_height = 30, 40

        for x, y, _ in self.tree_positions:
            tree_x = x * self.tile_size - (TREE_SIZE - TILE_SIZE) // 2
            tree_y = y * self.tile_size - (TREE_SIZE - TILE_SIZE) // 2
            trunk_x = tree_x + (TREE_SIZE - trunk_width) // 2
            trunk_y = tree_y + TREE_SIZE - trunk_height - 10
            rects.append(pygame.Rect(trunk_x, trunk_y, trunk_width, trunk_height))

        return rects

    def _setup_cats(self, positions):
        """Setup cats at predefined positions."""
        cats = []
        tree_tiles = set((x, y) for x, y, _ in self.tree_positions)

        for x, y in positions:
            if (x, y) not in tree_tiles:
                cat_idx = random.randrange(len(self.cat_images))
                cats.append((x, y, cat_idx))

        return cats

    def _generate_cats(self):
        """Generate cat positions on paths (fallback)."""
        cats = []
        tree_tiles = set((x, y) for x, y, _ in self.tree_positions)

        # Find all path positions
        path_positions = []
        for y in range(len(self.map_data)):
            for x in range(len(self.map_data[y])):
                if self.map_data[y][x] == 'path' and (x, y) not in tree_tiles:
                    path_positions.append((x, y))

        # Select spread out positions
        selected = []
        for _ in range(100):
            if len(selected) >= 3 or not path_positions:
                break
            pos = random.choice(path_positions)
            if all(abs(pos[0] - p[0]) + abs(pos[1] - p[1]) >= 8 for p in selected):
                selected.append(pos)

        for x, y in selected:
            cat_idx = random.randrange(len(self.cat_images))
            cats.append((x, y, cat_idx))

        return cats

    def check_tree_collision(self, player_rect):
        """Check if player collides with any tree trunk."""
        for rect in self.tree_collision_rects:
            if player_rect.colliderect(rect):
                return True
        return False

    def check_cat_proximity(self, player_rect):
        """Check if player is near a cat. Returns (index, cat_image_index) or (None, None)."""
        proximity = 60
        for i, (x, y, cat_idx) in enumerate(self.cat_positions):
            cat_center_x = x * self.tile_size
            cat_center_y = y * self.tile_size
            dist = ((cat_center_x - player_rect.centerx) ** 2 +
                    (cat_center_y - player_rect.centery) ** 2) ** 0.5
            if dist < proximity:
                return i, cat_idx
        return None, None

    def collect_cat(self, index):
        """Remove cat from map after collection."""
        if 0 <= index < len(self.cat_positions):
            return self.cat_positions.pop(index)
        return None

    def draw_base_map(self, screen, camera_offset):
        """Draw grass and path tiles."""
        for y, row in enumerate(self.map_data):
            for x, tile in enumerate(row):
                pos = (x * self.tile_size - camera_offset[0],
                       y * self.tile_size - camera_offset[1])
                img = self.path_image if tile == 'path' else self.tile_image
                screen.blit(img, pos)

    def draw_trees(self, screen, camera_offset):
        """Draw trees layer."""
        for x, y, tree_idx in self.tree_positions:
            pos = (x * self.tile_size - camera_offset[0] - (TREE_SIZE - TILE_SIZE) // 2,
                   y * self.tile_size - camera_offset[1] - (TREE_SIZE - TILE_SIZE) // 2)
            screen.blit(self.tree_images[tree_idx], pos)

    def draw_cats(self, screen, camera_offset):
        """Draw cats layer."""
        for x, y, cat_idx in self.cat_positions:
            pos = (x * self.tile_size - camera_offset[0] - TREE_SIZE // 4,
                   y * self.tile_size - camera_offset[1] - TREE_SIZE // 4)
            screen.blit(self.cat_images[cat_idx], pos)

    def draw_leaves(self, screen, camera_offset):
        """Draw animated leaves overlay."""
        current_time = pygame.time.get_ticks()
        if current_time - self.leaves_timer > self.leaves_speed:
            self.leaves_frame = (self.leaves_frame + 1) % len(self.leaves_animation)
            self.leaves_timer = current_time

        for y in range(0, self.map_height * self.tile_size, self.leaves_size):
            for x in range(0, self.map_width * self.tile_size, self.leaves_size):
                pos = (x - camera_offset[0], y - camera_offset[1])
                screen.blit(self.leaves_animation[self.leaves_frame], pos)

    def draw(self, screen, camera_offset, player):
        """Draw all background layers."""
        self.draw_base_map(screen, camera_offset)
        player.draw(screen, camera_offset)
        self.draw_trees(screen, camera_offset)
        self.draw_cats(screen, camera_offset)
