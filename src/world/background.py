import pygame
import random
import math
from src.ui.lore_display import create_placeholder
from src.ui.lore_data import CATS_LORE, COLLECTIBLES_LORE
from src.utils import get_image, get_cached_trees, set_cached_trees

# Constants
TILE_SIZE = 64
TREE_SIZE = 128
COLLECTIBLE_SIZE = 48

# Leaf particle colors (matching tree sprites)
LEAF_COLORS = [
    # Red/burgundy leaves (tree1)
    (139, 58, 58),    # Dark red
    (160, 70, 70),    # Medium red
    (120, 50, 50),    # Darker red
    (170, 85, 85),    # Light burgundy
    # Yellow/olive leaves (tree2)
    (155, 139, 59),   # Olive
    (170, 150, 70),   # Light olive
    (140, 125, 50),   # Dark olive
    (180, 160, 80),   # Yellow-ish
]


def load_graphics():
    """Load and scale all background graphics (uses cache)."""
    # Base tile
    tile_image = get_image('graphics/landscape/tile.png', (TILE_SIZE, TILE_SIZE))

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

    return tile_image, tree_images, path_image, cat_images, collectible_images


class LeafParticle:
    """A falling leaf particle in world coordinates."""
    def __init__(self, world_x, world_y, color):
        self.world_x = world_x
        self.world_y = world_y
        self.color = color
        self.size = random.randint(10, 18)
        self.fall_speed = random.uniform(25, 55)
        self.sway_speed = random.uniform(1.0, 3.0)
        self.sway_amplitude = random.uniform(20, 50)
        self.sway_offset = random.uniform(0, math.pi * 2)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-3, 3)
        self.time = random.uniform(0, 100)

    def update(self, dt):
        """Update particle position in world."""
        self.time += dt
        self.world_y += self.fall_speed * dt
        self.world_x += math.sin(self.time * self.sway_speed + self.sway_offset) * self.sway_amplitude * dt
        self.rotation += self.rotation_speed

    def draw(self, screen, camera_offset):
        """Draw the leaf particle."""
        screen_x = int(self.world_x - camera_offset[0])
        screen_y = int(self.world_y - camera_offset[1])

        angle_rad = math.radians(self.rotation)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        # Leaf shape (elongated)
        half_w = self.size // 3
        half_h = self.size // 2

        local_points = [
            (0, -half_h),
            (half_w, 0),
            (0, half_h),
            (-half_w, 0),
        ]

        points = []
        for px, py in local_points:
            rx = px * cos_a - py * sin_a
            ry = px * sin_a + py * cos_a
            points.append((screen_x + rx, screen_y + ry))

        pygame.draw.polygon(screen, self.color, points)

    def is_off_screen(self, camera_offset, screen_width, screen_height):
        """Check if particle is outside visible area."""
        screen_x = self.world_x - camera_offset[0]
        screen_y = self.world_y - camera_offset[1]
        margin = 100
        return (screen_x < -margin or screen_x > screen_width + margin or
                screen_y < -margin or screen_y > screen_height + margin)

    def is_in_cabin(self, cabin):
        """Check if leaf is inside cabin area."""
        if cabin is None:
            return False
        cabin_left = cabin.x * cabin.tile_size
        cabin_top = cabin.y * cabin.tile_size
        cabin_right = (cabin.x + cabin.width) * cabin.tile_size
        cabin_bottom = (cabin.y + cabin.height) * cabin.tile_size
        return (cabin_left < self.world_x < cabin_right and
                cabin_top < self.world_y < cabin_bottom)


class Background:
    def __init__(self, map_width, map_height, tile_size, screen_width, screen_height, cat_positions=None, collectible_positions=None, spawn_point=None, grid=None):
        self.tile_image, self.tree_images, self.path_image, self.cat_images, self.collectible_images = load_graphics()
        self.map_width = map_width
        self.map_height = map_height
        self.tile_size = tile_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.spawn_point = spawn_point or (map_width // 2, map_height // 2)

        # Leaf particles system
        self.leaf_particles = []
        self.leaf_count = 150  # Target number of leaves on screen

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

    def _is_in_cabin(self, world_x, world_y, cabin):
        """Check if position is inside cabin area."""
        if cabin is None:
            return False
        cabin_left = cabin.x * cabin.tile_size - 30
        cabin_top = cabin.y * cabin.tile_size - 30
        cabin_right = (cabin.x + cabin.width) * cabin.tile_size + 30
        cabin_bottom = (cabin.y + cabin.height) * cabin.tile_size + 30
        return cabin_left < world_x < cabin_right and cabin_top < world_y < cabin_bottom

    def _spawn_leaf_at_position(self, world_x, world_y, cabin):
        """Try to spawn a leaf at given position, avoiding cabin."""
        if self._is_in_cabin(world_x, world_y, cabin):
            return None
        color = random.choice(LEAF_COLORS)
        return LeafParticle(world_x, world_y, color)

    def _spawn_leaf_on_edge(self, camera_offset, cabin):
        """Spawn a leaf at random edge of visible area."""
        for _ in range(10):
            edge = random.randint(0, 3)  # 0=top, 1=bottom, 2=left, 3=right

            if edge == 0:  # Top edge
                world_x = camera_offset[0] + random.randint(0, self.screen_width)
                world_y = camera_offset[1] - random.randint(10, 50)
            elif edge == 1:  # Bottom edge
                world_x = camera_offset[0] + random.randint(0, self.screen_width)
                world_y = camera_offset[1] + self.screen_height + random.randint(10, 50)
            elif edge == 2:  # Left edge
                world_x = camera_offset[0] - random.randint(10, 50)
                world_y = camera_offset[1] + random.randint(0, self.screen_height)
            else:  # Right edge
                world_x = camera_offset[0] + self.screen_width + random.randint(10, 50)
                world_y = camera_offset[1] + random.randint(0, self.screen_height)

            leaf = self._spawn_leaf_at_position(world_x, world_y, cabin)
            if leaf:
                return leaf
        return None

    def _spawn_leaf_anywhere(self, camera_offset, cabin):
        """Spawn a leaf anywhere in visible area."""
        for _ in range(10):
            world_x = camera_offset[0] + random.randint(0, self.screen_width)
            world_y = camera_offset[1] + random.randint(0, self.screen_height)
            leaf = self._spawn_leaf_at_position(world_x, world_y, cabin)
            if leaf:
                return leaf
        return None

    def update_leaf_particles(self, dt, camera_offset, cabin=None):
        """Update leaf particles - respawn when off-screen or in cabin."""
        # Update existing particles
        for particle in self.leaf_particles:
            particle.update(dt)

        # Remove off-screen particles AND particles inside cabin
        self.leaf_particles = [
            p for p in self.leaf_particles
            if not p.is_off_screen(camera_offset, self.screen_width, self.screen_height)
            and not p.is_in_cabin(cabin)
        ]

        # Spawn new particles to maintain count
        while len(self.leaf_particles) < self.leaf_count:
            # If very few leaves, spawn anywhere on screen to fill quickly
            if len(self.leaf_particles) < self.leaf_count // 3:
                new_leaf = self._spawn_leaf_anywhere(camera_offset, cabin)
            else:
                # Normal: spawn at random edges
                new_leaf = self._spawn_leaf_on_edge(camera_offset, cabin)

            if new_leaf:
                self.leaf_particles.append(new_leaf)
            else:
                break

    def draw_leaf_particles(self, screen, camera_offset):
        """Draw all leaf particles."""
        for particle in self.leaf_particles:
            particle.draw(screen, camera_offset)

    def draw_cabin_arrow(self, screen, player_rect, cabin, camera_offset):
        """Draw a nice chevron arrow pointing to cabin when cabin is off-screen."""
        if cabin is None:
            return

        # Calculate cabin bounds in screen coordinates
        cabin_left = cabin.x * cabin.tile_size - camera_offset[0]
        cabin_top = cabin.y * cabin.tile_size - camera_offset[1]
        cabin_right = (cabin.x + cabin.width) * cabin.tile_size - camera_offset[0]
        cabin_bottom = (cabin.y + cabin.height) * cabin.tile_size - camera_offset[1]

        # Check if cabin is visible on screen (with some margin)
        margin = 50
        cabin_visible = (
            cabin_right > -margin and
            cabin_left < self.screen_width + margin and
            cabin_bottom > -margin and
            cabin_top < self.screen_height + margin
        )

        # Only show arrow if cabin is off-screen
        if cabin_visible:
            return

        # Calculate cabin center (door position)
        cabin_center_x = (cabin.x + cabin.width / 2) * cabin.tile_size
        cabin_center_y = (cabin.y + cabin.height) * cabin.tile_size  # Bottom of cabin (door)

        # Calculate direction from player to cabin
        player_center_x = player_rect.centerx
        player_center_y = player_rect.centery

        dx = cabin_center_x - player_center_x
        dy = cabin_center_y - player_center_y

        # Calculate angle to cabin
        angle = math.atan2(dy, dx)

        # Pulsing animation
        pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5  # 0 to 1
        pulse_offset = pulse * 8

        # Position arrow at edge of screen
        margin = 50
        half_w = self.screen_width // 2
        half_h = self.screen_height // 2

        # Calculate position on screen edge
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        # Find intersection with screen edge
        if abs(cos_a) > 0.001:
            t_x = (half_w - margin) / abs(cos_a) if cos_a > 0 else (half_w - margin) / abs(cos_a)
        else:
            t_x = float('inf')
        if abs(sin_a) > 0.001:
            t_y = (half_h - margin) / abs(sin_a) if sin_a > 0 else (half_h - margin) / abs(sin_a)
        else:
            t_y = float('inf')

        t = min(t_x, t_y)
        arrow_x = half_w + cos_a * (t - pulse_offset)
        arrow_y = half_h + sin_a * (t - pulse_offset)

        # Draw 3 chevrons (>>>) with fade effect
        chevron_size = 14
        chevron_spacing = 12

        for i in range(3):
            offset = i * chevron_spacing
            alpha = 255 - i * 60  # Fade out further chevrons

            cx = arrow_x - cos_a * offset
            cy = arrow_y - sin_a * offset

            # Chevron points (V shape pointing in direction)
            # Perpendicular direction
            perp_x = -sin_a
            perp_y = cos_a

            # Three points of chevron
            tip_x = cx + cos_a * chevron_size
            tip_y = cy + sin_a * chevron_size

            left_x = cx - cos_a * chevron_size * 0.3 + perp_x * chevron_size
            left_y = cy - sin_a * chevron_size * 0.3 + perp_y * chevron_size

            right_x = cx - cos_a * chevron_size * 0.3 - perp_x * chevron_size
            right_y = cy - sin_a * chevron_size * 0.3 - perp_y * chevron_size

            # Colors with pulse
            base_color = (255, 220, 150)
            glow_color = (255, 180, 100)
            color = tuple(int(base_color[j] * (0.7 + pulse * 0.3)) for j in range(3))

            # Draw thick chevron lines
            thickness = 4 if i == 0 else 3
            pygame.draw.line(screen, color, (left_x, left_y), (tip_x, tip_y), thickness)
            pygame.draw.line(screen, color, (right_x, right_y), (tip_x, tip_y), thickness)

            # Draw outline
            outline_color = (100, 70, 40)
            pygame.draw.line(screen, outline_color, (left_x, left_y), (tip_x, tip_y), 1)
            pygame.draw.line(screen, outline_color, (right_x, right_y), (tip_x, tip_y), 1)

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
