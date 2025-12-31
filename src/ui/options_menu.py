"""Options menu for Mind of Seasons."""

import pygame
import random
from src.utils import get_font, get_image
from src.save_system import load_settings, save_settings


class OptionsMenu:
    """Options menu for game settings."""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Fonts
        self.title_font = get_font(20)
        self.menu_font = get_font(12)
        self.small_font = get_font(10)

        # Menu state
        self.selected_index = 0
        self.is_showing = False

        # Settings
        self.settings = load_settings()

        # Options (label, key, type, min, max)
        self.options = [
            ("Fullscreen", "fullscreen", "toggle"),
            ("Master Volume", "master_volume", "slider", 0, 100),
            ("Music Volume", "music_volume", "slider", 0, 100),
            ("SFX Volume", "sfx_volume", "slider", 0, 100),
        ]

        # Input cooldown
        self.input_cooldown = 0

        # Track if fullscreen changed (needs restart/immediate apply)
        self.fullscreen_changed = False

        # Background
        self._init_background()

    def _init_background(self):
        """Initialize background with grass tiles and trees."""
        TILE_SIZE = 64
        TREE_SIZE = 128

        self.tile_image = get_image('graphics/landscape/tile.png', (TILE_SIZE, TILE_SIZE))
        self.tree_images = []
        for i in range(1, 3):
            tree_img = get_image(f'graphics/landscape/tree{i}.png', (TREE_SIZE, TREE_SIZE))
            if tree_img:
                self.tree_images.append(tree_img)

        random.seed(44)  # Different seed
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
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

    def show(self):
        """Show the options menu."""
        self.is_showing = True
        self.selected_index = 0
        self.input_cooldown = 15
        self.settings = load_settings()
        self.fullscreen_changed = False

    def hide(self):
        """Hide the options menu and save settings."""
        self.is_showing = False
        save_settings(self.settings)

    def update(self, keys, events):
        """
        Update options menu.

        Returns:
            tuple: (action, data) where action can be:
                - None: no action
                - "back": go back to previous menu
                - "toggle_fullscreen": toggle fullscreen mode
        """
        if not self.is_showing:
            return None, None

        # Input cooldown
        if self.input_cooldown > 0:
            self.input_cooldown -= 1
            return None, None

        # Navigation
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.selected_index = (self.selected_index - 1) % len(self.options)
            self.input_cooldown = 12
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.selected_index = (self.selected_index + 1) % len(self.options)
            self.input_cooldown = 12

        # Value adjustment
        option = self.options[self.selected_index]
        option_key = option[1]
        option_type = option[2]

        if option_type == "toggle":
            if keys[pygame.K_RETURN] or keys[pygame.K_SPACE] or keys[pygame.K_f] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                self.settings[option_key] = not self.settings[option_key]
                self.input_cooldown = 15
                if option_key == "fullscreen":
                    self.fullscreen_changed = True
                    return "toggle_fullscreen", self.settings[option_key]

        elif option_type == "slider":
            min_val, max_val = option[3], option[4]
            step = 5

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.settings[option_key] = max(min_val, self.settings[option_key] - step)
                self.input_cooldown = 8
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.settings[option_key] = min(max_val, self.settings[option_key] + step)
                self.input_cooldown = 8

        # Back
        if keys[pygame.K_ESCAPE]:
            self.hide()
            self.input_cooldown = 15
            return "back", None

        return None, None

    def draw(self, screen):
        """Draw the options menu."""
        if not self.is_showing:
            return

        # Draw background with trees
        self._draw_background(screen)

        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        # Title
        title_surface = self.title_font.render("OPTIONS", True, (200, 180, 140))
        title_rect = title_surface.get_rect(centerx=center_x, centery=center_y - 90)
        screen.blit(title_surface, title_rect)

        # Options
        start_y = center_y - 40
        for i, option in enumerate(self.options):
            label = option[0]
            key = option[1]
            opt_type = option[2]

            is_selected = (i == self.selected_index)
            label_color = (255, 220, 150) if is_selected else (180, 180, 190)

            # Label
            prefix = "> " if is_selected else "  "
            label_surface = self.menu_font.render(f"{prefix}{label}", True, label_color)
            label_rect = label_surface.get_rect(right=center_x - 20, centery=start_y + i * 35)
            screen.blit(label_surface, label_rect)

            # Value
            if opt_type == "toggle":
                value = self.settings.get(key, False)
                value_text = "ON" if value else "OFF"
                value_color = (100, 200, 100) if value else (200, 100, 100)
                value_surface = self.menu_font.render(value_text, True, value_color)
                value_rect = value_surface.get_rect(left=center_x + 20, centery=start_y + i * 35)
                screen.blit(value_surface, value_rect)

            elif opt_type == "slider":
                value = self.settings.get(key, 50)
                min_val, max_val = option[3], option[4]

                # Draw slider bar
                bar_x = center_x + 20
                bar_y = start_y + i * 35
                bar_width = 100
                bar_height = 8

                # Background
                pygame.draw.rect(screen, (60, 60, 70), (bar_x, bar_y - bar_height // 2, bar_width, bar_height), border_radius=4)

                # Fill
                fill_width = int(bar_width * value / max_val)
                if fill_width > 0:
                    fill_color = (180, 160, 100) if is_selected else (140, 130, 90)
                    pygame.draw.rect(screen, fill_color, (bar_x, bar_y - bar_height // 2, fill_width, bar_height), border_radius=4)

                # Value text
                value_surface = self.small_font.render(f"{value}%", True, (160, 160, 170))
                value_rect = value_surface.get_rect(left=bar_x + bar_width + 10, centery=bar_y)
                screen.blit(value_surface, value_rect)

        # Hint
        hint_text = "[ESC] Back"
        if self.options[self.selected_index][2] == "toggle":
            hint_text = "[SPACE] Toggle   " + hint_text
        else:
            hint_text = "[LEFT/RIGHT] Adjust   " + hint_text

        hint_surface = self.small_font.render(hint_text, True, (120, 120, 130))
        hint_rect = hint_surface.get_rect(centerx=center_x, centery=center_y + 90)
        screen.blit(hint_surface, hint_rect)

        # Note about volume (placeholder)
        note_surface = self.small_font.render("(Volume settings coming soon)", True, (100, 100, 110))
        note_rect = note_surface.get_rect(centerx=center_x, centery=center_y + 110)
        screen.blit(note_surface, note_rect)
