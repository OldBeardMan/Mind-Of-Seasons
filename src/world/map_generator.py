import random
import math


def generate_map(width, height, scale=15.0, octaves=4, num_cats=5, seed=None):
    """
    Generate terrain with cats spread across the map and paths connecting them.

    Args:
        width: Map width in tiles
        height: Map height in tiles
        scale: Perlin noise scale (unused, kept for compatibility)
        octaves: Perlin noise octaves (unused, kept for compatibility)
        num_cats: Number of cats to place
        seed: Optional seed for reproducible generation

    Returns: (grid, cat_positions, spawn_point, seed)
    """
    if seed is None:
        seed = random.randint(0, 999999)
    random.seed(seed)

    grid = [["0" for _ in range(width)] for _ in range(height)]

    # Divide map into sectors and place a cat in each sector
    margin = 4
    cat_positions = []

    # Calculate sector grid dynamically based on num_cats
    grid_size = max(3, int(math.ceil(math.sqrt(num_cats * 1.5))))
    cols = grid_size
    rows = grid_size
    sector_width = (width - 2 * margin) // cols
    sector_height = (height - 2 * margin) // rows

    sectors = []
    for row in range(rows):
        for col in range(cols):
            sx = margin + col * sector_width
            sy = margin + row * sector_height
            sectors.append((sx, sy, sx + sector_width, sy + sector_height))

    # Select random sectors for cats
    random.shuffle(sectors)
    selected_sectors = sectors[:num_cats]

    # Place cat at random position in each sector
    for sx, sy, ex, ey in selected_sectors:
        x = random.randint(sx + 2, ex - 2)
        y = random.randint(sy + 2, ey - 2)
        if 0 <= x < width and 0 <= y < height:
            cat_positions.append((x, y))

    # Player spawn point - center of map
    spawn_point = (width // 2, height // 2)

    # Points of interest = cat positions + player spawn
    pois = [spawn_point] + cat_positions

    # Connect spawn to cats and cats to each other
    for i in range(len(pois)):
        start = pois[i]
        end = pois[(i + 1) % len(pois)]
        _draw_path(grid, start, end, width, height)

    # Add a few extra connections between cats
    if len(cat_positions) > 2:
        extra_connections = random.randint(1, 2)
        for _ in range(extra_connections):
            start = random.choice(cat_positions)
            end = random.choice(cat_positions)
            if start != end:
                _draw_path(grid, start, end, width, height)

    return grid, cat_positions, spawn_point, seed


def _draw_path(grid, start, end, width, height):
    """
    Draw a natural-looking path between two points.
    Uses a modified line algorithm with random drift for organic appearance.
    """
    x1, y1 = start
    x2, y2 = end

    path_width = 1
    max_steps = width * height
    steps = 0

    while steps < max_steps:
        steps += 1

        # Draw path with width of 3 tiles
        for ox in range(-path_width, path_width + 1):
            for oy in range(-path_width, path_width + 1):
                if abs(ox) + abs(oy) <= path_width + 1:
                    nx, ny = x1 + ox, y1 + oy
                    if 0 <= nx < width and 0 <= ny < height:
                        grid[ny][nx] = "1"

        # Check if we reached the destination
        if abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1:
            break

        dx = x2 - x1
        dy = y2 - y1

        # Random drift for natural appearance
        if random.random() < 0.3:
            drift = random.choice([-1, 0, 0, 1])
            if abs(dx) > abs(dy):
                y1 += drift
            else:
                x1 += drift
            x1 = max(0, min(width - 1, x1))
            y1 = max(0, min(height - 1, y1))

        # Main movement towards target
        if abs(dx) > abs(dy):
            x1 += 1 if dx > 0 else -1
        elif dy != 0:
            y1 += 1 if dy > 0 else -1
        else:
            break


def map_initialization(width, height, num_cats=5, seed=None):
    """
    Initialize map by generating from seed.

    The map is always generated from seed - no file storage needed.
    The seed is stored in save files for persistence.

    Args:
        width: Map width in tiles
        height: Map height in tiles
        num_cats: Number of cats to place
        seed: Optional seed for reproducible generation

    Returns: (grid, cat_positions, spawn_point, seed)
    """
    grid, cat_positions, spawn_point, used_seed = generate_map(width, height, num_cats=num_cats, seed=seed)
    return grid, cat_positions, spawn_point, used_seed
