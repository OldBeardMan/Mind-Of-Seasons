"""Minimap with fog of war system."""

import pygame


class Minimap:
    """A minimap that reveals as the player explores."""

    def __init__(self, screen_width, screen_height, map_width, map_height, tile_size):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_width = map_width
        self.map_height = map_height
        self.tile_size = tile_size

        # Minimap display settings
        self.size = 180  # Minimap size in pixels
        self.margin = 15
        self.x = screen_width - self.size - self.margin
        self.y = self.margin

        # How many tiles player reveals around them (radius)
        self.reveal_radius = 8

        # Visited tiles set - stores (tile_x, tile_y) tuples
        self.visited_tiles = set()

        # Scale factor: how many map tiles per minimap pixel
        self.scale = self.size / max(map_width, map_height)

        # Colors
        self.color_fog = (20, 20, 30)  # Unexplored
        self.color_grass = (45, 65, 45)  # Explored grass
        self.color_path = (80, 70, 55)  # Explored path
        self.color_player = (255, 220, 100)  # Player position
        self.color_cabin = (180, 140, 100)  # Cabin
        self.color_cat = (255, 150, 180)  # Cat positions
        self.color_border = (60, 50, 40)
        self.color_bg = (15, 15, 20, 200)  # Semi-transparent background

        # Pre-render static elements
        self._surface = None
        self._needs_redraw = True

    def update_position(self, screen_width, screen_height):
        """Update minimap position when screen size changes."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = screen_width - self.size - self.margin
        self.y = self.margin

    def update(self, player_tile_x, player_tile_y):
        """Update visited tiles based on player position."""
        # Reveal tiles around player
        for dy in range(-self.reveal_radius, self.reveal_radius + 1):
            for dx in range(-self.reveal_radius, self.reveal_radius + 1):
                # Circular reveal
                if dx * dx + dy * dy <= self.reveal_radius * self.reveal_radius:
                    tx = player_tile_x + dx
                    ty = player_tile_y + dy
                    if 0 <= tx < self.map_width and 0 <= ty < self.map_height:
                        if (tx, ty) not in self.visited_tiles:
                            self.visited_tiles.add((tx, ty))
                            self._needs_redraw = True

    def set_visited_tiles(self, tiles):
        """Set visited tiles from saved data."""
        self.visited_tiles = set(tuple(t) for t in tiles)
        self._needs_redraw = True

    def get_visited_tiles(self):
        """Get visited tiles for saving."""
        return list(self.visited_tiles)

    def _world_to_minimap(self, tile_x, tile_y):
        """Convert world tile coordinates to minimap pixel coordinates."""
        mx = int(tile_x * self.scale)
        my = int(tile_y * self.scale)
        return mx, my

    def draw(self, screen, map_data, player_tile_x, player_tile_y, cabin=None, cat_positions=None):
        """Draw the minimap."""
        # Create surface with alpha
        surface = pygame.Surface((self.size + 4, self.size + 4), pygame.SRCALPHA)

        # Draw background
        pygame.draw.rect(surface, self.color_bg, (0, 0, self.size + 4, self.size + 4), border_radius=8)
        pygame.draw.rect(surface, self.color_border, (0, 0, self.size + 4, self.size + 4), 2, border_radius=8)

        # Offset for border
        offset = 2

        # Draw fog base
        pygame.draw.rect(surface, self.color_fog, (offset, offset, self.size, self.size))

        # Draw visited tiles
        for (tx, ty) in self.visited_tiles:
            if 0 <= ty < len(map_data) and 0 <= tx < len(map_data[0]):
                mx, my = self._world_to_minimap(tx, ty)
                tile_type = map_data[ty][tx]
                color = self.color_path if tile_type == 'path' else self.color_grass

                # Draw pixel (or small rect if scale > 1)
                pixel_size = max(1, int(self.scale))
                pygame.draw.rect(surface, color, (offset + mx, offset + my, pixel_size, pixel_size))

        # Draw cabin if visible
        if cabin is not None:
            cabin_tx, cabin_ty = cabin.x, cabin.y
            # Check if any part of cabin is discovered
            cabin_visible = any(
                (cabin_tx + dx, cabin_ty + dy) in self.visited_tiles
                for dx in range(cabin.width)
                for dy in range(cabin.height)
            )
            if cabin_visible:
                mx, my = self._world_to_minimap(cabin_tx, cabin_ty)
                cabin_w = max(3, int(cabin.width * self.scale))
                cabin_h = max(3, int(cabin.height * self.scale))
                pygame.draw.rect(surface, self.color_cabin, (offset + mx, offset + my, cabin_w, cabin_h))

        # Draw discovered cats
        if cat_positions:
            for (cx, cy, _) in cat_positions:
                if (cx, cy) in self.visited_tiles:
                    mx, my = self._world_to_minimap(cx, cy)
                    pygame.draw.circle(surface, self.color_cat, (offset + mx, offset + my), 3)

        # Draw player position (always visible, pulsing)
        px, py = self._world_to_minimap(player_tile_x, player_tile_y)
        pulse = (pygame.time.get_ticks() % 1000) / 1000
        player_size = 3 + int(pulse * 2)
        pygame.draw.circle(surface, self.color_player, (offset + px, offset + py), player_size)

        # Draw border highlight
        pygame.draw.rect(surface, (80, 70, 60), (0, 0, self.size + 4, self.size + 4), 1, border_radius=8)

        # Blit to screen
        screen.blit(surface, (self.x, self.y))

        # Draw "MAP" label
        try:
            font = pygame.font.Font(None, 18)
            label = font.render("MAP", True, (150, 140, 130))
            screen.blit(label, (self.x + self.size // 2 - label.get_width() // 2, self.y + self.size + 6))
        except:
            pass
