"""Main menu screen for Mind of Seasons."""

import pygame
import random
from src.utils import get_font, get_image
from src.save_system import list_saves, delete_save


# Game constants
GAME_VERSION = "alpha 1.0.0"
GAME_TITLE = "Mind of Seasons"
STUDIO_NAME = "MKGames"


class MainMenu:
    """Main menu with navigation and save slot selection."""

    # Menu states
    STATE_MAIN = "main"
    STATE_SAVE_SELECT = "save_select"
    STATE_CONFIRM_DELETE = "confirm_delete"
    STATE_CONFIRM_OVERWRITE = "confirm_overwrite"

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Fonts
        self.title_font = get_font(36)
        self.version_font = get_font(10)
        self.menu_font = get_font(16)
        self.small_font = get_font(12)
        self.link_font = get_font(9)

        # Menu state
        self.state = self.STATE_MAIN
        self.selected_index = 0
        self.is_loading_mode = False  # True when loading, False when starting new game

        # Main menu options
        self.main_options = ["New Game", "Load Game", "Options", "Credits", "Quit"]

        # Save slots
        self.save_slots = []
        self.selected_slot = 0
        self.slot_to_delete = None
        self.slot_to_overwrite = None

        # Input cooldown
        self.input_cooldown = 0

        # Animation
        self.anim_timer = 0

        # Background graphics
        self._init_background()

    def _init_background(self):
        """Initialize background with grass tiles and trees."""
        TILE_SIZE = 64
        TREE_SIZE = 128

        # Load graphics
        self.tile_image = get_image('graphics/landscape/tile.png', (TILE_SIZE, TILE_SIZE))
        self.tree_images = []
        for i in range(1, 3):
            tree_img = get_image(f'graphics/landscape/tree{i}.png', (TREE_SIZE, TREE_SIZE))
            if tree_img:
                self.tree_images.append(tree_img)

        # Generate random tree positions (seeded for consistency)
        random.seed(42)
        self.tree_positions = []
        num_trees = (self.screen_width * self.screen_height) // 40000  # ~1 tree per 200x200 area
        for _ in range(max(5, num_trees)):
            x = random.randint(-TREE_SIZE // 2, self.screen_width - TREE_SIZE // 2)
            y = random.randint(-TREE_SIZE // 2, self.screen_height - TREE_SIZE // 2)
            tree_idx = random.randint(0, len(self.tree_images) - 1) if self.tree_images else 0
            self.tree_positions.append((x, y, tree_idx))

        self.tile_size = TILE_SIZE
        self.tree_size = TREE_SIZE

    def refresh_saves(self):
        """Refresh save slot information."""
        self.save_slots = list_saves()

    def update(self, keys, events):
        """
        Update menu state.

        Returns:
            tuple: (action, data) where action can be:
                - None: no action
                - "new_game": start new game, data = slot number
                - "load_game": load game, data = slot number
                - "options": open options
                - "credits": open credits
                - "quit": quit game
        """
        self.anim_timer += 1

        # Input cooldown
        if self.input_cooldown > 0:
            self.input_cooldown -= 1
            return None, None

        # Handle different states
        if self.state == self.STATE_MAIN:
            return self._update_main_menu(keys, events)
        elif self.state == self.STATE_SAVE_SELECT:
            return self._update_save_select(keys, events)
        elif self.state == self.STATE_CONFIRM_DELETE:
            return self._update_confirm_delete(keys, events)
        elif self.state == self.STATE_CONFIRM_OVERWRITE:
            return self._update_confirm_overwrite(keys, events)

        return None, None

    def reset_cooldown(self):
        """Reset input cooldown (call when returning to main menu)."""
        self.input_cooldown = 20

    def _update_main_menu(self, keys, events):
        """Update main menu navigation."""
        # Navigation
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.selected_index = (self.selected_index - 1) % len(self.main_options)
            self.input_cooldown = 12
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.selected_index = (self.selected_index + 1) % len(self.main_options)
            self.input_cooldown = 12

        # Selection
        if keys[pygame.K_RETURN] or keys[pygame.K_SPACE] or keys[pygame.K_f]:
            self.input_cooldown = 15
            option = self.main_options[self.selected_index]

            if option == "New Game":
                self.is_loading_mode = False
                self.refresh_saves()
                self.state = self.STATE_SAVE_SELECT
                self.selected_slot = 0
            elif option == "Load Game":
                self.is_loading_mode = True
                self.refresh_saves()
                # Check if any saves exist
                if any(slot is not None for slot in self.save_slots):
                    self.state = self.STATE_SAVE_SELECT
                    # Select first non-empty slot
                    for i, slot in enumerate(self.save_slots):
                        if slot is not None:
                            self.selected_slot = i
                            break
            elif option == "Options":
                return "options", None
            elif option == "Credits":
                return "credits", None
            elif option == "Quit":
                return "quit", None

        # ESC to quit from main menu
        if keys[pygame.K_ESCAPE]:
            return "quit", None

        return None, None

    def _update_save_select(self, keys, events):
        """Update save slot selection."""
        # Navigation
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self._navigate_slots(-1)
            self.input_cooldown = 12
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self._navigate_slots(1)
            self.input_cooldown = 12

        # Selection
        if keys[pygame.K_RETURN] or keys[pygame.K_SPACE] or keys[pygame.K_f]:
            self.input_cooldown = 15
            slot_info = self.save_slots[self.selected_slot]

            if self.is_loading_mode:
                # Load existing game
                if slot_info is not None:
                    return "load_game", self.selected_slot + 1
            else:
                # New game
                if slot_info is None:
                    # Empty slot - start new game
                    return "new_game", self.selected_slot + 1
                else:
                    # Slot has data - confirm overwrite
                    self.slot_to_overwrite = self.selected_slot + 1
                    self.state = self.STATE_CONFIRM_OVERWRITE

        # Delete save (D key)
        if keys[pygame.K_d]:
            slot_info = self.save_slots[self.selected_slot]
            if slot_info is not None:
                self.slot_to_delete = self.selected_slot + 1
                self.state = self.STATE_CONFIRM_DELETE
                self.input_cooldown = 15

        # Back
        if keys[pygame.K_ESCAPE]:
            self.state = self.STATE_MAIN
            self.input_cooldown = 15

        return None, None

    def _navigate_slots(self, direction):
        """Navigate save slots, skipping empty slots in load mode."""
        if self.is_loading_mode:
            # Find next non-empty slot
            for _ in range(3):
                self.selected_slot = (self.selected_slot + direction) % 3
                if self.save_slots[self.selected_slot] is not None:
                    break
        else:
            self.selected_slot = (self.selected_slot + direction) % 3

    def _update_confirm_delete(self, keys, events):
        """Update delete confirmation dialog."""
        if keys[pygame.K_RETURN] or keys[pygame.K_y]:
            # Confirm delete
            delete_save(self.slot_to_delete)
            self.refresh_saves()
            self.slot_to_delete = None
            self.state = self.STATE_SAVE_SELECT
            self.input_cooldown = 15
        elif keys[pygame.K_ESCAPE] or keys[pygame.K_n]:
            # Cancel
            self.slot_to_delete = None
            self.state = self.STATE_SAVE_SELECT
            self.input_cooldown = 15

        return None, None

    def _update_confirm_overwrite(self, keys, events):
        """Update overwrite confirmation dialog."""
        if keys[pygame.K_RETURN] or keys[pygame.K_y]:
            # Confirm overwrite - start new game
            slot = self.slot_to_overwrite
            self.slot_to_overwrite = None
            self.state = self.STATE_MAIN
            self.input_cooldown = 15
            return "new_game", slot
        elif keys[pygame.K_ESCAPE] or keys[pygame.K_n]:
            # Cancel
            self.slot_to_overwrite = None
            self.state = self.STATE_SAVE_SELECT
            self.input_cooldown = 15

        return None, None

    def draw(self, screen):
        """Draw the menu."""
        # Draw grass background
        self._draw_background(screen)

        # Draw based on state
        if self.state == self.STATE_MAIN:
            self._draw_main_menu(screen)
        elif self.state == self.STATE_SAVE_SELECT:
            self._draw_save_select(screen)
        elif self.state == self.STATE_CONFIRM_DELETE:
            self._draw_save_select(screen)
            self._draw_confirm_dialog(screen, "Delete this save?", "[Y] Yes  [N] No")
        elif self.state == self.STATE_CONFIRM_OVERWRITE:
            self._draw_save_select(screen)
            self._draw_confirm_dialog(screen, "Overwrite this save?", "[Y] Yes  [N] No")

    def _draw_background(self, screen):
        """Draw grass tiles and trees background."""
        # Draw grass tiles
        if self.tile_image:
            for y in range(0, self.screen_height + self.tile_size, self.tile_size):
                for x in range(0, self.screen_width + self.tile_size, self.tile_size):
                    screen.blit(self.tile_image, (x, y))
        else:
            screen.fill((60, 80, 50))  # Fallback green color

        # Draw trees
        if self.tree_images:
            for x, y, tree_idx in self.tree_positions:
                if tree_idx < len(self.tree_images):
                    screen.blit(self.tree_images[tree_idx], (x, y))

        # Dark overlay for readability
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

    def _draw_main_menu(self, screen):
        """Draw main menu."""
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        # Title
        title_surface = self.title_font.render(GAME_TITLE.upper(), True, (200, 180, 140))
        title_rect = title_surface.get_rect(centerx=center_x, centery=center_y - 100)
        screen.blit(title_surface, title_rect)

        # Version
        version_surface = self.version_font.render(GAME_VERSION, True, (120, 120, 130))
        version_rect = version_surface.get_rect(centerx=center_x, centery=center_y - 70)
        screen.blit(version_surface, version_rect)

        # Menu options
        start_y = center_y - 20
        for i, option in enumerate(self.main_options):
            is_selected = (i == self.selected_index)

            # Color and indicator
            if is_selected:
                color = (255, 220, 150)
                prefix = "> "
            else:
                color = (180, 180, 190)
                prefix = "  "

            text = f"{prefix}{option}"
            option_surface = self.menu_font.render(text, True, color)
            option_rect = option_surface.get_rect(centerx=center_x, centery=start_y + i * 30)
            screen.blit(option_surface, option_rect)

        # Footer - studio name
        footer_y = self.screen_height - 30
        studio_surface = self.small_font.render(STUDIO_NAME, True, (150, 140, 120))
        studio_rect = studio_surface.get_rect(centerx=center_x, centery=footer_y)
        screen.blit(studio_surface, studio_rect)

    def _draw_save_select(self, screen):
        """Draw save slot selection screen."""
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        # Title
        title_text = "Load Game" if self.is_loading_mode else "Select Save Slot"
        title_surface = self.menu_font.render(title_text, True, (200, 180, 140))
        title_rect = title_surface.get_rect(centerx=center_x, centery=center_y - 110)
        screen.blit(title_surface, title_rect)

        # Save slots
        slot_height = 60
        slot_width = 250
        start_y = center_y - 70

        for i, slot_info in enumerate(self.save_slots):
            is_selected = (i == self.selected_slot)
            slot_y = start_y + i * (slot_height + 10)

            # Slot background
            bg_color = (60, 55, 70) if is_selected else (40, 40, 50)
            border_color = (180, 160, 120) if is_selected else (80, 80, 90)

            slot_rect = pygame.Rect(center_x - slot_width // 2, slot_y, slot_width, slot_height)
            pygame.draw.rect(screen, bg_color, slot_rect, border_radius=6)
            pygame.draw.rect(screen, border_color, slot_rect, 2, border_radius=6)

            # Slot content
            if slot_info is None:
                # Empty slot
                if self.is_loading_mode:
                    text_color = (80, 80, 90)
                    status_text = "Empty"
                else:
                    text_color = (150, 150, 160) if is_selected else (120, 120, 130)
                    status_text = "New Game"

                status_surface = self.small_font.render(f"Slot {i + 1}: {status_text}", True, text_color)
                status_rect = status_surface.get_rect(centerx=center_x, centery=slot_y + slot_height // 2)
                screen.blit(status_surface, status_rect)
            else:
                # Slot with data
                text_color = (200, 200, 210) if is_selected else (160, 160, 170)

                # Slot number and kittens
                cats_text = f"{slot_info['stored_cats']}/{slot_info['total_cats']} Kittens"
                if slot_info['is_complete']:
                    cats_text += " *"

                slot_title = f"Slot {i + 1}: {cats_text}"
                title_surface = self.small_font.render(slot_title, True, text_color)
                title_rect = title_surface.get_rect(centerx=center_x, centery=slot_y + 20)
                screen.blit(title_surface, title_rect)

                # Play time
                time_text = f"Time: {slot_info['play_time_formatted']}"
                time_surface = self.link_font.render(time_text, True, (140, 140, 150))
                time_rect = time_surface.get_rect(centerx=center_x, centery=slot_y + 42)
                screen.blit(time_surface, time_rect)

        # Hints
        hint_y = start_y + 3 * (slot_height + 10) + 20
        back_hint = self.link_font.render("[ESC] Back", True, (120, 120, 130))
        back_rect = back_hint.get_rect(centerx=center_x - 60, centery=hint_y)
        screen.blit(back_hint, back_rect)

        # Delete hint (only if slot has data)
        if self.save_slots[self.selected_slot] is not None:
            delete_hint = self.link_font.render("[D] Delete", True, (150, 100, 100))
            delete_rect = delete_hint.get_rect(centerx=center_x + 60, centery=hint_y)
            screen.blit(delete_hint, delete_rect)

    def _draw_confirm_dialog(self, screen, title, hint):
        """Draw confirmation dialog overlay."""
        # Darken background
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        # Dialog box
        dialog_width = 280
        dialog_height = 80
        dialog_rect = pygame.Rect(center_x - dialog_width // 2, center_y - dialog_height // 2,
                                   dialog_width, dialog_height)
        pygame.draw.rect(screen, (50, 50, 60), dialog_rect, border_radius=8)
        pygame.draw.rect(screen, (180, 160, 120), dialog_rect, 2, border_radius=8)

        # Title
        title_surface = self.small_font.render(title, True, (220, 200, 160))
        title_rect = title_surface.get_rect(centerx=center_x, centery=center_y - 15)
        screen.blit(title_surface, title_rect)

        # Hint
        hint_surface = self.link_font.render(hint, True, (160, 160, 170))
        hint_rect = hint_surface.get_rect(centerx=center_x, centery=center_y + 15)
        screen.blit(hint_surface, hint_rect)
