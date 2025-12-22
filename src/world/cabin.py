import pygame

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

    # Bed - rustic style
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

    # Coffee machine - rustic kettle/pot style
    coffee = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    coffee.fill((0, 0, 0, 0))
    # Stolik
    pygame.draw.rect(coffee, (100, 70, 45), (8, 40, 48, 24))
    # Kociołek/czajnik
    pygame.draw.ellipse(coffee, (60, 55, 50), (16, 20, 32, 28))
    pygame.draw.ellipse(coffee, (50, 45, 42), (20, 24, 24, 20))
    # Uchwyt
    pygame.draw.arc(coffee, (70, 60, 55), (38, 22, 16, 20), -1.5, 1.5, 3)
    # Para
    pygame.draw.line(coffee, (200, 200, 200), (28, 18), (26, 10), 2)
    pygame.draw.line(coffee, (200, 200, 200), (36, 18), (38, 8), 2)
    tiles['coffee'] = coffee

    return tiles


class Cabin:
    def __init__(self, spawn_x, spawn_y, tile_size=64):
        self.tile_size = tile_size
        self.tiles = create_cabin_tiles()

        # Cabin dimensions (in tiles)
        self.width = 6  # tiles
        self.height = 5  # tiles

        # Position cabin so spawn point is in front of door
        # Door is at bottom center of cabin
        self.x = spawn_x - self.width // 2  # Center horizontally on spawn
        self.y = spawn_y - self.height - 1  # Cabin above spawn point

        # Define cabin layout (0=floor, 1=wall, 2=door, 3=roof)
        self.layout = [
            [3, 3, 3, 3, 3, 3],  # Roof (top row - visual only)
            [1, 0, 0, 0, 0, 1],  # Wall | floor floor floor floor | Wall
            [1, 0, 0, 0, 0, 1],  # Wall | floor floor floor floor | Wall
            [1, 0, 0, 0, 0, 1],  # Wall | floor floor floor floor | Wall
            [1, 1, 2, 2, 1, 1],  # Wall Wall Door Door Wall Wall
        ]

        # Furniture positions (relative to cabin top-left, in tiles)
        self.bed_pos = (1, 1)      # Top-left inside
        self.coffee_pos = (4, 1)   # Top-right inside

        # Build collision rects for walls
        self.wall_rects = self._build_wall_collisions()

        # Sprytek position (in front of door, to the left)
        self.sprytek_tile_x = spawn_x - 1
        self.sprytek_tile_y = spawn_y + 1

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

    def check_collision(self, player_rect):
        """Check if player collides with cabin walls."""
        for wall_rect in self.wall_rects:
            if player_rect.colliderect(wall_rect):
                return True
        return False

    def get_sprytek_position(self):
        """Get world position for Sprytek (in pixels)."""
        return (self.sprytek_tile_x * self.tile_size, self.sprytek_tile_y * self.tile_size)

    def get_bounds(self):
        """Get cabin bounding box in tile coordinates (for tree removal)."""
        return (self.x - 1, self.y - 1, self.x + self.width + 1, self.y + self.height + 2)

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

    def draw_upper(self, screen, camera_offset):
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
        screen.blit(self.tiles['coffee'], (coffee_world_x - camera_offset[0], coffee_world_y - camera_offset[1]))
