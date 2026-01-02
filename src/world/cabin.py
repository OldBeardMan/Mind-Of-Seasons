import pygame
import random

TILE_SIZE = 64


def create_cabin_tiles():
    """Create placeholder tiles for cabin elements.

    Kolorystyka - naturalne, ziemiste kolory pasujace do pixel-art lasu:
    - Podloga: ciepłe drewno
    - Sciany: ciemne drewno/bale
    - Dach: sloma/trzcina
    """
    tiles = {}

    # Floor tile - warm wood (ciepłe drewno)
    floor = pygame.Surface((TILE_SIZE, TILE_SIZE))
    floor.fill((160, 120, 80))  # Ciepły brąz
    pygame.draw.line(floor, (130, 95, 60), (0, TILE_SIZE//2), (TILE_SIZE, TILE_SIZE//2), 2)
    pygame.draw.line(floor, (140, 105, 70), (TILE_SIZE//3, 0), (TILE_SIZE//3, TILE_SIZE), 1)
    pygame.draw.line(floor, (140, 105, 70), (2*TILE_SIZE//3, 0), (2*TILE_SIZE//3, TILE_SIZE), 1)
    tiles['floor'] = floor

    # Wall tile - dark wood logs (ciemne bale drewna)
    wall = pygame.Surface((TILE_SIZE, TILE_SIZE))
    wall.fill((90, 65, 45))  # Ciemny brąz
    # Linie belek
    pygame.draw.rect(wall, (75, 55, 35), (0, 0, TILE_SIZE, TILE_SIZE//3))
    pygame.draw.rect(wall, (85, 60, 40), (0, TILE_SIZE//3, TILE_SIZE, TILE_SIZE//3))
    pygame.draw.rect(wall, (70, 50, 32), (0, 2*TILE_SIZE//3, TILE_SIZE, TILE_SIZE//3))
    pygame.draw.line(wall, (60, 42, 28), (0, TILE_SIZE//3), (TILE_SIZE, TILE_SIZE//3), 2)
    pygame.draw.line(wall, (60, 42, 28), (0, 2*TILE_SIZE//3), (TILE_SIZE, 2*TILE_SIZE//3), 2)
    tiles['wall'] = wall

    # Roof tile - thatch/straw (sloma)
    roof = pygame.Surface((TILE_SIZE, TILE_SIZE))
    roof.fill((140, 115, 70))  # Słomiany kolor
    for i in range(0, TILE_SIZE, 8):
        pygame.draw.line(roof, (120, 95, 55), (0, i), (TILE_SIZE, i + 4), 2)
        pygame.draw.line(roof, (155, 130, 85), (0, i + 4), (TILE_SIZE, i), 1)
    tiles['roof'] = roof

    # Door tile - wooden door
    door = pygame.Surface((TILE_SIZE, TILE_SIZE))
    door.fill((100, 70, 45))
    pygame.draw.rect(door, (85, 60, 38), (6, 2, TILE_SIZE-12, TILE_SIZE-4))
    pygame.draw.line(door, (70, 48, 30), (TILE_SIZE//2, 4), (TILE_SIZE//2, TILE_SIZE-4), 2)
    pygame.draw.circle(door, (180, 150, 80), (TILE_SIZE-14, TILE_SIZE//2), 4)  # Klamka
    tiles['door'] = door

    # Bed - rustic style (2 tiles wide)
    bed = pygame.Surface((TILE_SIZE * 2, TILE_SIZE), pygame.SRCALPHA)
    bed.fill((0, 0, 0, 0))
    # Rama lozka (drewno)
    pygame.draw.rect(bed, (100, 70, 45), (0, 8, TILE_SIZE * 2, TILE_SIZE - 8))
    # Materac (len/plotno)
    pygame.draw.rect(bed, (190, 175, 145), (4, 12, TILE_SIZE * 2 - 8, TILE_SIZE - 22))
    # Poduszka
    pygame.draw.rect(bed, (210, 200, 170), (8, 16, 36, 26))
    # Koc (welna)
    pygame.draw.rect(bed, (120, 90, 70), (48, 16, TILE_SIZE * 2 - 56, TILE_SIZE - 30))
    tiles['bed'] = bed

    # Coffee machine - espresso machine style
    coffee = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    coffee.fill((0, 0, 0, 0))

    # Table/counter
    pygame.draw.rect(coffee, (100, 70, 45), (4, 48, 56, 16))
    pygame.draw.rect(coffee, (80, 55, 35), (4, 48, 56, 4))

    # Machine body (centered)
    pygame.draw.rect(coffee, (70, 65, 60), (16, 12, 32, 38))  # Main body
    pygame.draw.rect(coffee, (85, 80, 75), (18, 14, 28, 34))  # Front panel
    pygame.draw.rect(coffee, (50, 45, 40), (16, 8, 32, 6))    # Top

    # Drip tray area
    pygame.draw.rect(coffee, (40, 35, 30), (20, 42, 24, 8))

    # Cup slot (dark opening)
    pygame.draw.rect(coffee, (30, 25, 20), (24, 30, 16, 14))

    # Portafilter handle
    pygame.draw.rect(coffee, (60, 50, 40), (22, 26, 20, 4))
    pygame.draw.circle(coffee, (50, 40, 30), (42, 28), 4)

    # Buttons/controls
    pygame.draw.circle(coffee, (180, 50, 50), (24, 18), 3)  # Red button
    pygame.draw.circle(coffee, (50, 150, 50), (34, 18), 3)  # Green button

    # Steam (subtle)
    pygame.draw.line(coffee, (200, 200, 200), (28, 8), (26, 2), 2)
    pygame.draw.line(coffee, (200, 200, 200), (36, 8), (38, 2), 2)

    tiles['coffee'] = coffee

    # Cat bed/cushion - wygodne legowisko dla kotka
    cat_bed = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    cat_bed.fill((0, 0, 0, 0))
    # Podstawa koszyka
    pygame.draw.ellipse(cat_bed, (140, 100, 60), (4, 20, 56, 40))
    # Wnetrze koszyka (miekkie)
    pygame.draw.ellipse(cat_bed, (180, 150, 120), (10, 26, 44, 28))
    # Poduszeczka
    pygame.draw.ellipse(cat_bed, (200, 180, 150), (14, 30, 36, 20))
    # Obramowanie koszyka
    pygame.draw.arc(cat_bed, (100, 70, 45), (4, 20, 56, 40), 3.14, 6.28, 3)
    tiles['cat_bed'] = cat_bed

    return tiles


class Cabin:
    def __init__(self, spawn_x, spawn_y, tile_size=64):
        self.tile_size = tile_size
        self.tiles = create_cabin_tiles()

        # Cabin dimensions (in tiles) - duza chatka
        self.width = 10  # tiles
        self.height = 9  # tiles

        # Position cabin so spawn point is in front of door
        # Door is at bottom center of cabin
        self.x = spawn_x - self.width // 2  # Center horizontally on spawn
        self.y = spawn_y - self.height - 1  # Cabin above spawn point

        # Define cabin layout (0=floor, 1=wall, 2=door, 3=roof)
        self.layout = [
            [3, 3, 3, 3, 3, 3, 3, 3, 3, 3],  # Roof
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Wall | floor x8 | Wall
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Wall | floor x8 | Wall
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Wall | floor x8 | Wall
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Wall | floor x8 | Wall
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Wall | floor x8 | Wall
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Wall | floor x8 | Wall
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Wall | floor x8 | Wall
            [1, 1, 1, 1, 2, 2, 1, 1, 1, 1],  # Wall x4 Door Door Wall x4
        ]

        # Furniture positions (relative to cabin top-left, in tiles)
        self.bed_pos = (1, 1)      # Top-left inside (2 tiles wide)
        self.coffee_pos = (8, 1)   # Top-right inside

        # Cat bed positions (5 beds along left wall)
        self.cat_bed_positions = [
            (1, 3),   # Left wall - top
            (1, 4),   # Left wall - upper-mid
            (1, 5),   # Left wall - middle
            (1, 6),   # Left wall - lower-mid
            (1, 7),   # Left wall - bottom
        ]

        # Build collision rects for walls AND furniture
        self.wall_rects = self._build_wall_collisions()
        self.furniture_rects = self._build_furniture_collisions()

        # Sprytek position (in front of door, to the left)
        self.sprytek_tile_x = spawn_x - 1
        self.sprytek_tile_y = spawn_y + 1

        # Storage system - tylko kotki (na legowiskach)
        self.stored_cats = []  # Lista indeksów przechowywanych kotków

    def _build_wall_collisions(self):
        """Build collision rectangles for walls."""
        rects = []
        for row_idx, row in enumerate(self.layout):
            for col_idx, tile_type in enumerate(row):
                if tile_type == 1:  # Wall
                    world_x = (self.x + col_idx) * self.tile_size
                    world_y = (self.y + row_idx) * self.tile_size
                    rects.append(pygame.Rect(world_x, world_y, self.tile_size, self.tile_size))
                elif tile_type == 3:  # Roof (also collision)
                    world_x = (self.x + col_idx) * self.tile_size
                    world_y = (self.y + row_idx) * self.tile_size
                    rects.append(pygame.Rect(world_x, world_y, self.tile_size, self.tile_size))
        return rects

    def _build_furniture_collisions(self):
        """Build collision rectangles for furniture (bed, coffee, cat beds)."""
        rects = []
        # Bed collision (2 tiles wide)
        bed_x = (self.x + self.bed_pos[0]) * self.tile_size
        bed_y = (self.y + self.bed_pos[1]) * self.tile_size
        rects.append(pygame.Rect(bed_x, bed_y, self.tile_size * 2, self.tile_size))

        # Coffee/kettle collision
        coffee_x = (self.x + self.coffee_pos[0]) * self.tile_size
        coffee_y = (self.y + self.coffee_pos[1]) * self.tile_size
        rects.append(pygame.Rect(coffee_x, coffee_y, self.tile_size, self.tile_size))

        # Cat beds collision
        for (bx, by) in self.cat_bed_positions:
            cat_bed_x = (self.x + bx) * self.tile_size
            cat_bed_y = (self.y + by) * self.tile_size
            rects.append(pygame.Rect(cat_bed_x, cat_bed_y, self.tile_size, self.tile_size))

        return rects

    def check_collision(self, player_rect):
        """Check if player collides with cabin walls or furniture."""
        # Check walls
        for wall_rect in self.wall_rects:
            if player_rect.colliderect(wall_rect):
                return True
        # Check furniture
        for furn_rect in self.furniture_rects:
            if player_rect.colliderect(furn_rect):
                return True
        return False

    def get_sprytek_position(self):
        """Get world position for Sprytek (in pixels)."""
        return (self.sprytek_tile_x * self.tile_size, self.sprytek_tile_y * self.tile_size)

    def get_bounds(self):
        """Get cabin bounding box in tile coordinates (for tree removal).
        Extended by 2 tiles in each direction to create clear path around cabin."""
        return (self.x - 3, self.y - 3, self.x + self.width + 3, self.y + self.height + 4)

    def is_player_inside(self, player_rect):
        """Check if player is inside the cabin (on floor tiles)."""
        # Wewnętrzny obszar chatki (bez ścian i dachu)
        inner_left = (self.x + 1) * self.tile_size
        inner_right = (self.x + self.width - 1) * self.tile_size
        inner_top = (self.y + 1) * self.tile_size
        inner_bottom = (self.y + self.height - 1) * self.tile_size

        cabin_interior = pygame.Rect(inner_left, inner_top,
                                      inner_right - inner_left,
                                      inner_bottom - inner_top)
        return cabin_interior.colliderect(player_rect)

    def store_cat(self, cat_index):
        """Store a cat in the cabin. Returns True if successful."""
        if len(self.stored_cats) < 5 and cat_index not in self.stored_cats:
            self.stored_cats.append(cat_index)
            return True
        return False

    def get_stored_cat_count(self):
        """Return count of stored cats."""
        return len(self.stored_cats)

    def get_coffee_machine_world_pos(self):
        """Get coffee machine position in world pixels."""
        coffee_x = (self.x + self.coffee_pos[0]) * self.tile_size + self.tile_size // 2
        coffee_y = (self.y + self.coffee_pos[1]) * self.tile_size + self.tile_size // 2
        return (coffee_x, coffee_y)

    def is_near_coffee_machine(self, player_rect):
        """Check if player is near the coffee machine."""
        coffee_pos = self.get_coffee_machine_world_pos()
        player_center = player_rect.center
        dx = coffee_pos[0] - player_center[0]
        dy = coffee_pos[1] - player_center[1]
        distance = (dx * dx + dy * dy) ** 0.5
        return distance < 80  # 80px proximity radius

    def draw_floor(self, screen, camera_offset):
        """Draw cabin floor layer (under player)."""
        for row_idx, row in enumerate(self.layout):
            for col_idx, tile_type in enumerate(row):
                world_x = (self.x + col_idx) * self.tile_size
                world_y = (self.y + row_idx) * self.tile_size
                screen_x = world_x - camera_offset[0]
                screen_y = world_y - camera_offset[1]

                if tile_type == 0 or tile_type == 2:  # Floor or Door area
                    screen.blit(self.tiles['floor'], (screen_x, screen_y))

    def draw_upper(self, screen, camera_offset, cat_images=None, is_brewing=False, brew_progress=0):
        """Draw cabin walls, roof, and furniture (over player)."""
        for row_idx, row in enumerate(self.layout):
            for col_idx, tile_type in enumerate(row):
                world_x = (self.x + col_idx) * self.tile_size
                world_y = (self.y + row_idx) * self.tile_size
                screen_x = world_x - camera_offset[0]
                screen_y = world_y - camera_offset[1]

                if tile_type == 1:  # Wall
                    screen.blit(self.tiles['wall'], (screen_x, screen_y))
                elif tile_type == 3:  # Roof
                    screen.blit(self.tiles['roof'], (screen_x, screen_y))

        # Draw furniture
        # Bed (2 tiles wide)
        bed_world_x = (self.x + self.bed_pos[0]) * self.tile_size
        bed_world_y = (self.y + self.bed_pos[1]) * self.tile_size
        screen.blit(self.tiles['bed'], (bed_world_x - camera_offset[0], bed_world_y - camera_offset[1]))

        # Coffee kettle
        coffee_world_x = (self.x + self.coffee_pos[0]) * self.tile_size
        coffee_world_y = (self.y + self.coffee_pos[1]) * self.tile_size
        coffee_screen_x = coffee_world_x - camera_offset[0]
        coffee_screen_y = coffee_world_y - camera_offset[1]
        screen.blit(self.tiles['coffee'], (coffee_screen_x, coffee_screen_y))

        # Draw brewing animation
        if is_brewing:
            self._draw_brewing_animation(screen, coffee_screen_x, coffee_screen_y, brew_progress)

        # Draw cat beds (legowiska pod ścianą)
        for i, (bx, by) in enumerate(self.cat_bed_positions):
            bed_world_x = (self.x + bx) * self.tile_size
            bed_world_y = (self.y + by) * self.tile_size
            screen.blit(self.tiles['cat_bed'], (bed_world_x - camera_offset[0], bed_world_y - camera_offset[1]))

            # Draw stored cat on this bed if present
            if cat_images and i < len(self.stored_cats):
                cat_index = self.stored_cats[i]
                if cat_index < len(cat_images):
                    cat_x = bed_world_x + 8
                    cat_y = bed_world_y - 12
                    screen.blit(cat_images[cat_index], (cat_x - camera_offset[0], cat_y - camera_offset[1]))

    def _draw_brewing_animation(self, screen, coffee_x, coffee_y, progress):
        """Draw steam and progress bar for brewing coffee."""
        # Steam particles (more intense during brewing)
        steam_center_x = coffee_x + 32
        steam_base_y = coffee_y + 18

        for i in range(5):
            # Random offset for each steam particle
            x_offset = random.randint(-8, 8)
            y_offset = random.randint(0, 20)

            # Particle size varies
            size = random.randint(2, 4)

            # Draw steam particle
            pygame.draw.circle(screen, (220, 220, 220),
                             (steam_center_x + x_offset, steam_base_y - y_offset), size)

        # Progress bar above coffee machine
        bar_width = 50
        bar_height = 8
        bar_x = coffee_x + 7
        bar_y = coffee_y - 15

        # Background
        pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height), border_radius=3)

        # Fill (brown coffee color)
        fill_width = int(bar_width * progress)
        if fill_width > 0:
            pygame.draw.rect(screen, (139, 90, 43), (bar_x, bar_y, fill_width, bar_height), border_radius=3)

        # Border
        pygame.draw.rect(screen, (100, 80, 60), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=3)
