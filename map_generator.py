import random
import os
from noise import pnoise2


def generate_map(width, height, scale=15.0, octaves=4, num_cats=5):
    """
    Generate terrain with cats spread across the map and paths connecting them.
    Uses Perlin Noise to find optimal locations for cats in each sector.

    Returns: (grid, cat_positions, spawn_point)
    """
    seed = random.randint(0, 1000)
    grid = [["0" for _ in range(width)] for _ in range(height)]

    # Generate base terrain with Perlin Noise
    noise_map = []
    for y in range(height):
        row = []
        for x in range(width):
            value = pnoise2(x / scale, y / scale, octaves=octaves, base=seed)
            normalized = (value + 1) / 2
            row.append(normalized)
        noise_map.append(row)

    # Divide map into sectors and place a cat in each sector
    margin = 4
    cat_positions = []

    # Calculate sector grid (3x2 for 5-6 cats)
    cols = 3
    rows = 2
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

    # Find best position in each sector using noise
    for sx, sy, ex, ey in selected_sectors:
        best_pos = None
        best_noise = -1

        for _ in range(10):
            x = random.randint(sx + 2, ex - 2)
            y = random.randint(sy + 2, ey - 2)
            if 0 <= x < width and 0 <= y < height:
                noise_val = noise_map[y][x]
                if noise_val > best_noise:
                    best_noise = noise_val
                    best_pos = (x, y)

        if best_pos:
            cat_positions.append(best_pos)

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

    return grid, cat_positions, spawn_point


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


def _save_grid(grid, filename):
    """Save map grid to file."""
    with open(filename, "w") as f:
        for row in grid:
            f.write(''.join(str(cell) for cell in row) + "\n")


def _save_map_data(cat_positions, spawn_point, filename):
    """Save cat positions and spawn point to file."""
    with open(filename, "w") as f:
        f.write(f"spawn:{spawn_point[0]},{spawn_point[1]}\n")
        for x, y in cat_positions:
            f.write(f"cat:{x},{y}\n")


def _load_map_data(filename):
    """Load cat positions and spawn point from file."""
    cat_positions = []
    spawn_point = None
    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("spawn:"):
                    coords = line[6:].split(",")
                    spawn_point = (int(coords[0]), int(coords[1]))
                elif line.startswith("cat:"):
                    coords = line[4:].split(",")
                    cat_positions.append((int(coords[0]), int(coords[1])))
    except FileNotFoundError:
        pass
    return cat_positions, spawn_point


def map_initialization(width, height, map_file="map.txt", data_file="map_data.txt", num_cats=5):
    """
    Initialize map. Generates new map if it doesn't exist.

    Returns: (cat_positions, spawn_point)
    """
    if not os.path.isfile(map_file):
        grid, cat_positions, spawn_point = generate_map(width, height, num_cats=num_cats)
        _save_grid(grid, map_file)
        _save_map_data(cat_positions, spawn_point, data_file)
        return cat_positions, spawn_point

    return _load_map_data(data_file)
