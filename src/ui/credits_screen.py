"""Credits screen for Mind of Seasons."""

import pygame
import random
from src.utils import get_font, get_image
from src.ui.main_menu import GAME_VERSION, GAME_TITLE, STUDIO_NAME
from src.config import TILE_SIZE


class CreditsScreen:
    """Credits screen showing game information and credits."""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Fonts
        self.title_font = get_font(28)
        self.heading_font = get_font(14)
        self.text_font = get_font(12)
        self.small_font = get_font(10)
        self.link_font = get_font(9)

        # State
        self.is_showing = False
        self.input_cooldown = 0

        # Background
        self._init_background()

    def _init_background(self):
        """Initialize background with grass tiles and trees."""
        TREE_SIZE = 128

        self.tile_image = get_image('graphics/landscape/tile.png', (TILE_SIZE, TILE_SIZE))
        self.tree_images = []
        for i in range(1, 3):
            tree_img = get_image(f'graphics/landscape/tree{i}.png', (TREE_SIZE, TREE_SIZE))
            if tree_img:
                self.tree_images.append(tree_img)

        random.seed(43)  # Different seed than main menu
        self.tree_positions = []
        num_trees = (self.screen_width * self.screen_height) // 40000
        for _ in range(max(5, num_trees)):
            x = random.randint(-TREE_SIZE // 2, self.screen_width - TREE_SIZE // 2)
            y = random.randint(-TREE_SIZE // 2, self.screen_height - TREE_SIZE // 2)
            tree_idx = random.randint(0, len(self.tree_images) - 1) if self.tree_images else 0
            self.tree_positions.append((x, y, tree_idx))

        self.tile_size = TILE_SIZE

    def _draw_background(self, screen):
        """Draw grass tiles and trees background."""
        if self.tile_image:
            for y in range(0, self.screen_height + self.tile_size, self.tile_size):
                for x in range(0, self.screen_width + self.tile_size, self.tile_size):
                    screen.blit(self.tile_image, (x, y))
        else:
            screen.fill((60, 80, 50))

        if self.tree_images:
            for x, y, tree_idx in self.tree_positions:
                if tree_idx < len(self.tree_images):
                    screen.blit(self.tree_images[tree_idx], (x, y))

        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

    def show(self):
        """Show the credits screen."""
        self.is_showing = True
        self.input_cooldown = 30

    def hide(self):
        """Hide the credits screen."""
        self.is_showing = False

    def update(self, keys, events):
        """
        Update credits screen.

        Returns:
            "back" if user wants to go back, None otherwise
        """
        if not self.is_showing:
            return None

        # Input cooldown
        if self.input_cooldown > 0:
            self.input_cooldown -= 1
            return None

        # Any key to go back
        if any(keys) or any(event.type == pygame.KEYDOWN for event in events):
            self.hide()
            return "back"

        return None

    def draw(self, screen):
        """Draw the credits screen."""
        if not self.is_showing:
            return

        # Draw background with trees
        self._draw_background(screen)

        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        # Title
        title_surface = self.title_font.render(GAME_TITLE.upper(), True, (200, 180, 140))
        title_rect = title_surface.get_rect(centerx=center_x, centery=center_y - 110)
        screen.blit(title_surface, title_rect)

        # Version
        version_surface = self.small_font.render(GAME_VERSION, True, (140, 140, 150))
        version_rect = version_surface.get_rect(centerx=center_x, centery=center_y - 85)
        screen.blit(version_surface, version_rect)

        # Created by
        created_surface = self.heading_font.render("Created by", True, (160, 160, 170))
        created_rect = created_surface.get_rect(centerx=center_x, centery=center_y - 50)
        screen.blit(created_surface, created_rect)

        # Author name
        author_surface = self.text_font.render("Matt Krupa", True, (220, 200, 160))
        author_rect = author_surface.get_rect(centerx=center_x, centery=center_y - 25)
        screen.blit(author_surface, author_rect)

        # Studio name
        studio_surface = self.heading_font.render(STUDIO_NAME, True, (180, 160, 120))
        studio_rect = studio_surface.get_rect(centerx=center_x, centery=center_y + 5)
        screen.blit(studio_surface, studio_rect)

        # Graphics by
        gfx_label = self.heading_font.render("Graphics by", True, (160, 160, 170))
        gfx_label_rect = gfx_label.get_rect(centerx=center_x, centery=center_y + 40)
        screen.blit(gfx_label, gfx_label_rect)

        gfx_name = self.text_font.render("wool", True, (220, 200, 160))
        gfx_name_rect = gfx_name.get_rect(centerx=center_x, centery=center_y + 65)
        screen.blit(gfx_name, gfx_name_rect)

        # Made with
        tech_surface = self.small_font.render("Made with Python & Pygame", True, (120, 120, 130))
        tech_rect = tech_surface.get_rect(centerx=center_x, centery=center_y + 100)
        screen.blit(tech_surface, tech_rect)

        # Hint to go back
        hint_surface = self.link_font.render("Press any key to return", True, (100, 100, 110))
        hint_rect = hint_surface.get_rect(centerx=center_x, centery=self.screen_height - 30)
        screen.blit(hint_surface, hint_rect)
