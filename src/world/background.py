import pygame
import random
from src.ui.lore_display import create_placeholder
from src.ui.lore_data import CATS_LORE, COLLECTIBLES_LORE
from src.utils import get_image, get_cached_trees, set_cached_trees

# Constants
TILE_SIZE = 64
TREE_SIZE = 128
COLLECTIBLE_SIZE = 48


def load_graphics():
    """Load and scale all background graphics (uses cache)."""
    # Base tile
    tile_image = get_image('graphics/landscape/tile.png', (TILE_SIZE, TILE_SIZE))

    # Animated leaves
    leaves_animation = []
    for i in range(5):
        leaves_img = get_image(f'graphics/landscape/leaves/{i}.png', (128, 128))
        leaves_animation.append(leaves_img)

    # Trees
    tree_images = []
    for i in range(1, 3):
        tree_img = get_image(f'graphics/landscape/tree{i}.png', (TREE_SIZE, TREE_SIZE))
        tree_images.append(tree_img)

    # Path
    path_image = get_image('graphics/landscape/path.png', (TILE_SIZE, TILE_SIZE))

    # Cats - load existing images or create placeholders for 5 lore cats
    cat_images = []
    for cat in CATS_LORE:
        if "image" in cat:
            cat_img = get_image(f'graphics/npc/{cat["image"]}', (TREE_SIZE // 2, TREE_SIZE // 2))
            if cat_img is None:
                cat_img = create_placeholder((TREE_SIZE // 2, TREE_SIZE // 2), cat["color"], cat["name"])
        else:
            cat_img = create_placeholder((TREE_SIZE // 2, TREE_SIZE // 2), cat["color"], cat["name"])
        cat_images.append(cat_img)

    # Collectibles - load image if available, otherwise placeholder
    collectible_images = []
    for item in COLLECTIBLES_LORE:
        if "image" in item:
            coll_img = get_image(f'graphics/landscape/{item["image"]}', (COLLECTIBLE_SIZE, COLLECTIBLE_SIZE))
            if coll_img is None:
                coll_img = create_placeholder((COLLECTIBLE_SIZE, COLLECTIBLE_SIZE), item["color"], item["name"])
        else:
            coll_img = create_placeholder((COLLECTIBLE_SIZE, COLLECTIBLE_SIZE), item["color"], item["name"])
        collectible_images.append(coll_img)

    return tile_image, leaves_animation, tree_images, path_image, cat_images, collectible_images


class Background:
    def __init__(self, map_width, map_height, tile_size, screen_width, screen_height, cat_positions=None, collectible_positions=None, spawn_point=None, grid=None):
        self.tile_image, self.leaves_animation, self.tree_images, self.path_image, self.cat_images, self.collectible_images = load_graphics()
        self.map_width = map_width
        self.map_height = map_height
        self.tile_size = tile_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.spawn_point = spawn_point or (map_width // 2, map_height // 2)

        # Leaves animation
        self.leaves_size = 128
        self.leaves_frame = 0
        self.leaves_timer = 0
        self.leaves_speed = 200

        # Spatial partitioning chunk size (in tiles)
        self.chunk_size = 16

        # Convert grid to map_data format
        self.map_data = self._convert_grid(grid)

        # Cache key includes spawn_point for cabin clearing
        cache_key = (map_width, map_height, spawn_point)
        cached = get_cached_trees(cache_key)
        if cached:
            # Use cached trees (already cleared around cabin)
            self.tree_positions = cached['trees'][:]
            self.tree_chunks = {k: v[:] for k, v in cached['tree_chunks'].items()}
            self.collision_chunks = {k: v[:] for k, v in cached['collision_chunks'].items()}
            self._trees_cache_used = True
        else:
            self.tree_positions = self._generate_trees()
            self.tree_chunks = self._build_tree_chunks()
            self.collision_chunks = self._build_collision_chunks()
            self._trees_cache_used = False

        self.cat_positions = self._setup_cats(cat_positions) if cat_positions else self._generate_cats()
        self.collectible_positions = self._setup_collectibles(collectible_positions) if collectible_positions else self._generate_collectibles()

    def _convert_grid(self, grid):
        """Convert grid (0/1 strings) to map_data format (path/grass)."""
        if grid is None:
            return []
        return [['path' if cell == '1' else 'grass' for cell in row] for row in grid]

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

    def clear_trees_in_area(self, min_x, min_y, max_x, max_y):
        """Remove trees in specified area and rebuild chunks."""
        # Skip if cache was used (trees already cleared)
        if getattr(self, '_trees_cache_used', False):
            return

        self.tree_positions = [
            (x, y, idx) for x, y, idx in self.tree_positions
            if not (min_x <= x <= max_x and min_y <= y <= max_y)
        ]
        # Rebuild chunks
        self.tree_chunks = self._build_tree_chunks()
        self.collision_chunks = self._build_collision_chunks()

        # Cache the result for future respawns
        cache_key = (self.map_width, self.map_height, self.spawn_point)
        set_cached_trees(cache_key, self.tree_positions, self.tree_chunks, self.collision_chunks)

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
        """Setup cats at predefined positions. Each cat gets unique lore index (0-4)."""
        cats = []
        tree_tiles = set((x, y) for x, y, _ in self.tree_positions)

        # Only use first 5 positions for lore cats
        valid_positions = [(x, y) for x, y in positions if (x, y) not in tree_tiles][:5]

        for i, (x, y) in enumerate(valid_positions):
            # Each cat has unique lore index (0-4)
            cats.append((x, y, i))

        return cats

    def _generate_cats(self):
        """Generate cat positions on paths (fallback). Only 5 lore cats."""
        cats = []
        tree_tiles = set((x, y) for x, y, _ in self.tree_positions)

        # Find all path positions
        path_positions = []
        for y in range(len(self.map_data)):
            for x in range(len(self.map_data[y])):
                if self.map_data[y][x] == 'path' and (x, y) not in tree_tiles:
                    path_positions.append((x, y))

        # Select spread out positions for 5 cats
        selected = []
        for _ in range(500):
            if len(selected) >= 5 or not path_positions:
                break
            pos = random.choice(path_positions)
            if all(abs(pos[0] - p[0]) + abs(pos[1] - p[1]) >= 15 for p in selected):
                selected.append(pos)

        # Each cat gets unique lore index (0-4)
        for i, (x, y) in enumerate(selected):
            cats.append((x, y, i))

        return cats

    def _setup_collectibles(self, positions):
        """Setup collectibles at predefined positions."""
        collectibles = []
        tree_tiles = set((x, y) for x, y, _ in self.tree_positions)
        cat_tiles = set((x, y) for x, y, _ in self.cat_positions)

        valid_positions = [(x, y) for x, y in positions if (x, y) not in tree_tiles and (x, y) not in cat_tiles][:10]

        for i, (x, y) in enumerate(valid_positions):
            collectibles.append((x, y, i))

        return collectibles

    def _generate_collectibles(self):
        """Generate collectible positions on paths (fallback). 10 items."""
        collectibles = []
        tree_tiles = set((x, y) for x, y, _ in self.tree_positions)
        cat_tiles = set((x, y) for x, y, _ in self.cat_positions)
        min_distance_from_spawn = 20  # tiles

        # Find all path positions not occupied and far from spawn
        path_positions = []
        for y in range(len(self.map_data)):
            for x in range(len(self.map_data[y])):
                if self.map_data[y][x] == 'path' and (x, y) not in tree_tiles and (x, y) not in cat_tiles:
                    # Check distance from spawn
                    dist_from_spawn = ((x - self.spawn_point[0]) ** 2 + (y - self.spawn_point[1]) ** 2) ** 0.5
                    if dist_from_spawn > min_distance_from_spawn:
                        path_positions.append((x, y))

        # Select spread out positions for 10 collectibles
        selected = []
        for _ in range(1000):
            if len(selected) >= 10 or not path_positions:
                break
            pos = random.choice(path_positions)
            # Ensure spacing from other collectibles and cats
            if all(abs(pos[0] - p[0]) + abs(pos[1] - p[1]) >= 12 for p in selected):
                if all(abs(pos[0] - c[0]) + abs(pos[1] - c[1]) >= 8 for c in [(cx, cy) for cx, cy, _ in self.cat_positions]):
                    selected.append(pos)

        for i, (x, y) in enumerate(selected):
            collectibles.append((x, y, i))

        return collectibles

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

    def check_collectible_proximity(self, player_rect):
        """Check if player is near a collectible. Returns (index, collectible_index) or (None, None)."""
        proximity = 50
        for i, (x, y, coll_idx) in enumerate(self.collectible_positions):
            coll_center_x = x * self.tile_size
            coll_center_y = y * self.tile_size
            dist = ((coll_center_x - player_rect.centerx) ** 2 +
                    (coll_center_y - player_rect.centery) ** 2) ** 0.5
            if dist < proximity:
                return i, coll_idx
        return None, None

    def collect_collectible(self, index):
        """Remove collectible from map after collection."""
        if 0 <= index < len(self.collectible_positions):
            return self.collectible_positions.pop(index)
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

    def draw_collectibles(self, screen, camera_offset):
        """Draw collectibles layer."""
        for x, y, coll_idx in self.collectible_positions:
            pos = (x * self.tile_size - camera_offset[0] - COLLECTIBLE_SIZE // 2,
                   y * self.tile_size - camera_offset[1] - COLLECTIBLE_SIZE // 2)
            screen.blit(self.collectible_images[coll_idx], pos)

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

    def draw(self, screen, camera_offset, player, cabin=None, enemy_manager=None, is_brewing=False, brew_progress=0):
        """Draw all background layers."""
        self.draw_base_map(screen, camera_offset)
        # Cabin floor (under player)
        if cabin:
            cabin.draw_floor(screen, camera_offset)
        player.draw(screen, camera_offset)
        # Enemies drawn at same layer as player (under trees)
        if enemy_manager:
            enemy_manager.draw(screen, camera_offset)
        self.draw_trees(screen, camera_offset)
        # Cabin walls/roof/furniture (over player when inside)
        if cabin:
            cabin.draw_upper(screen, camera_offset, self.cat_images, is_brewing, brew_progress)
        self.draw_cats(screen, camera_offset)
        self.draw_collectibles(screen, camera_offset)
