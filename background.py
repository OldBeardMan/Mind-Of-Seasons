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

        # Spatial partitioning chunk size (in tiles)
        self.chunk_size = 16

        # Load map and generate elements
        self.map_data = self._load_map(MAP_FILE)
        self.tree_positions = self._generate_trees()
        self.tree_chunks = self._build_tree_chunks()
        self.collision_chunks = self._build_collision_chunks()
        self.cat_positions = self._setup_cats(cat_positions) if cat_positions else self._generate_cats()

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

    def _build_tree_chunks(self):
        """Build spatial chunks for trees."""
        chunks = {}
        for x, y, tree_idx in self.tree_positions:
            chunk_x = x // self.chunk_size
            chunk_y = y // self.chunk_size
            key = (chunk_x, chunk_y)
            if key not in chunks:
                chunks[key] = []
            chunks[key].append((x, y, tree_idx))
        return chunks

    def _build_collision_chunks(self):
        """Build spatial chunks for tree collision rects."""
        chunks = {}
        trunk_width, trunk_height = 30, 40

        for x, y, _ in self.tree_positions:
            tree_x = x * self.tile_size - (TREE_SIZE - TILE_SIZE) // 2
            tree_y = y * self.tile_size - (TREE_SIZE - TILE_SIZE) // 2
            trunk_x = tree_x + (TREE_SIZE - trunk_width) // 2
            trunk_y = tree_y + TREE_SIZE - trunk_height - 10
            rect = pygame.Rect(trunk_x, trunk_y, trunk_width, trunk_height)

            chunk_x = x // self.chunk_size
            chunk_y = y // self.chunk_size
            key = (chunk_x, chunk_y)
            if key not in chunks:
                chunks[key] = []
            chunks[key].append(rect)
        return chunks

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
        """Check if player collides with any tree trunk (using spatial chunks)."""
        # Get player position in tile coordinates
        player_tile_x = player_rect.centerx // self.tile_size
        player_tile_y = player_rect.centery // self.tile_size

        # Check only nearby chunks (player chunk and adjacent)
        chunk_x = player_tile_x // self.chunk_size
        chunk_y = player_tile_y // self.chunk_size

        for dx in range(-1, 2):
            for dy in range(-1, 2):
                key = (chunk_x + dx, chunk_y + dy)
                if key in self.collision_chunks:
                    for rect in self.collision_chunks[key]:
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
        """Draw grass and path tiles (only visible ones)."""
        # Calculate visible tile range
        start_x = max(0, camera_offset[0] // self.tile_size)
        start_y = max(0, camera_offset[1] // self.tile_size)
        end_x = min(len(self.map_data[0]) if self.map_data else 0,
                    (camera_offset[0] + self.screen_width) // self.tile_size + 2)
        end_y = min(len(self.map_data),
                    (camera_offset[1] + self.screen_height) // self.tile_size + 2)

        for y in range(start_y, end_y):
            row = self.map_data[y]
            for x in range(start_x, min(end_x, len(row))):
                tile = row[x]
                pos = (x * self.tile_size - camera_offset[0],
                       y * self.tile_size - camera_offset[1])
                img = self.path_image if tile == 'path' else self.tile_image
                screen.blit(img, pos)

    def draw_trees(self, screen, camera_offset):
        """Draw trees layer (only visible chunks)."""
        # Calculate visible chunk range
        start_chunk_x = (camera_offset[0] // self.tile_size) // self.chunk_size - 1
        start_chunk_y = (camera_offset[1] // self.tile_size) // self.chunk_size - 1
        end_chunk_x = ((camera_offset[0] + self.screen_width) // self.tile_size) // self.chunk_size + 2
        end_chunk_y = ((camera_offset[1] + self.screen_height) // self.tile_size) // self.chunk_size + 2

        for chunk_y in range(start_chunk_y, end_chunk_y):
            for chunk_x in range(start_chunk_x, end_chunk_x):
                key = (chunk_x, chunk_y)
                if key not in self.tree_chunks:
                    continue
                for x, y, tree_idx in self.tree_chunks[key]:
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
        """Draw animated leaves overlay only in visible area."""
        current_time = pygame.time.get_ticks()
        if current_time - self.leaves_timer > self.leaves_speed:
            self.leaves_frame = (self.leaves_frame + 1) % len(self.leaves_animation)
            self.leaves_timer = current_time

        # Calculate visible area bounds
        start_x = (camera_offset[0] // self.leaves_size) * self.leaves_size
        start_y = (camera_offset[1] // self.leaves_size) * self.leaves_size
        end_x = camera_offset[0] + self.screen_width + self.leaves_size
        end_y = camera_offset[1] + self.screen_height + self.leaves_size

        for y in range(start_y, end_y, self.leaves_size):
            for x in range(start_x, end_x, self.leaves_size):
                pos = (x - camera_offset[0], y - camera_offset[1])
                screen.blit(self.leaves_animation[self.leaves_frame], pos)

    def draw(self, screen, camera_offset, player):
        """Draw all background layers."""
        self.draw_base_map(screen, camera_offset)
        player.draw(screen, camera_offset)
        self.draw_trees(screen, camera_offset)
        self.draw_cats(screen, camera_offset)
