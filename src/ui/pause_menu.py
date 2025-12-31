"""Pause menu for Mind of Seasons."""

import pygame
from src.utils import get_font
from src.ui.main_menu import GAME_VERSION


class PauseMenu:
    """Pause menu displayed when ESC is pressed during gameplay."""

    # Menu states
    STATE_MAIN = "main"
    STATE_CONFIRM_QUIT = "confirm_quit"
    STATE_CONFIRM_MENU = "confirm_menu"

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Fonts
        self.title_font = get_font(24)
        self.menu_font = get_font(14)
        self.small_font = get_font(10)

        # Menu state
        self.state = self.STATE_MAIN
        self.selected_index = 0
        self.is_showing = False

        # Menu options
        self.options = ["Resume", "Save Game", "Options", "Main Menu", "Quit"]

        # Input cooldown
        self.input_cooldown = 0

        # Save feedback
        self.save_message = ""
        self.save_message_timer = 0

    def show(self):
        """Show the pause menu."""
        self.is_showing = True
        self.state = self.STATE_MAIN
        self.selected_index = 0
        self.input_cooldown = 15

    def hide(self):
        """Hide the pause menu."""
        self.is_showing = False

    def show_save_message(self, success):
        """Show save feedback message."""
        self.save_message = "Game Saved!" if success else "Save Failed!"
        self.save_message_timer = 90  # 1.5 seconds at 60fps

    def update(self, keys, events):
        """
        Update pause menu.

        Returns:
            tuple: (action, data) where action can be:
                - None: no action
                - "resume": resume game
                - "save": save game
                - "options": open options
                - "main_menu": return to main menu
                - "quit": quit game
        """
        if not self.is_showing:
            return None, None

        # Update save message timer
        if self.save_message_timer > 0:
            self.save_message_timer -= 1
            if self.save_message_timer == 0:
                self.save_message = ""

        # Input cooldown
        if self.input_cooldown > 0:
            self.input_cooldown -= 1
            return None, None

        # Handle states
        if self.state == self.STATE_MAIN:
            return self._update_main(keys)
        elif self.state == self.STATE_CONFIRM_QUIT:
            return self._update_confirm_quit(keys)
        elif self.state == self.STATE_CONFIRM_MENU:
            return self._update_confirm_menu(keys)

        return None, None

    def _update_main(self, keys):
        """Update main pause menu."""
        # Navigation
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.selected_index = (self.selected_index - 1) % len(self.options)
            self.input_cooldown = 12
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.selected_index = (self.selected_index + 1) % len(self.options)
            self.input_cooldown = 12

        # Selection
        if keys[pygame.K_RETURN] or keys[pygame.K_SPACE] or keys[pygame.K_f]:
            self.input_cooldown = 15
            option = self.options[self.selected_index]

            if option == "Resume":
                self.hide()
                return "resume", None
            elif option == "Save Game":
                return "save", None
            elif option == "Options":
                return "options", None
            elif option == "Main Menu":
                self.state = self.STATE_CONFIRM_MENU
            elif option == "Quit":
                self.state = self.STATE_CONFIRM_QUIT

        # ESC to resume
        if keys[pygame.K_ESCAPE]:
            self.hide()
            self.input_cooldown = 15
            return "resume", None

        return None, None

    def _update_confirm_quit(self, keys):
        """Update quit confirmation."""
        if keys[pygame.K_RETURN] or keys[pygame.K_y]:
            self.input_cooldown = 15
            return "quit", None
        elif keys[pygame.K_ESCAPE] or keys[pygame.K_n]:
            self.state = self.STATE_MAIN
            self.input_cooldown = 15

        return None, None

    def _update_confirm_menu(self, keys):
        """Update main menu confirmation."""
        if keys[pygame.K_RETURN] or keys[pygame.K_y]:
            self.hide()
            self.input_cooldown = 15
            return "main_menu", None
        elif keys[pygame.K_ESCAPE] or keys[pygame.K_n]:
            self.state = self.STATE_MAIN
            self.input_cooldown = 15

        return None, None

    def draw(self, screen):
        """Draw the pause menu."""
        if not self.is_showing:
            return

        # Dark overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        # Title
        title_surface = self.title_font.render("PAUSED", True, (200, 180, 140))
        title_rect = title_surface.get_rect(centerx=center_x, centery=center_y - 80)
        screen.blit(title_surface, title_rect)

        # Menu options
        start_y = center_y - 30
        for i, option in enumerate(self.options):
            is_selected = (i == self.selected_index)

            if is_selected:
                color = (255, 220, 150)
                prefix = "> "
            else:
                color = (180, 180, 190)
                prefix = "  "

            text = f"{prefix}{option}"
            option_surface = self.menu_font.render(text, True, color)
            option_rect = option_surface.get_rect(centerx=center_x, centery=start_y + i * 25)
            screen.blit(option_surface, option_rect)

        # Save message
        if self.save_message:
            msg_color = (100, 200, 100) if "Saved" in self.save_message else (200, 100, 100)
            msg_surface = self.small_font.render(self.save_message, True, msg_color)
            msg_rect = msg_surface.get_rect(centerx=center_x, centery=center_y + 100)
            screen.blit(msg_surface, msg_rect)

        # Version in corner
        version_surface = self.small_font.render(GAME_VERSION, True, (80, 80, 90))
        screen.blit(version_surface, (10, self.screen_height - 20))

        # Draw confirmation dialog if needed
        if self.state == self.STATE_CONFIRM_QUIT:
            self._draw_confirm_dialog(screen, "Quit game?", "Unsaved progress lost!")
        elif self.state == self.STATE_CONFIRM_MENU:
            self._draw_confirm_dialog(screen, "Return to menu?", "Unsaved progress lost!")

    def _draw_confirm_dialog(self, screen, title, subtitle):
        """Draw confirmation dialog."""
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        # Dialog box
        dialog_width = 280
        dialog_height = 100
        dialog_rect = pygame.Rect(center_x - dialog_width // 2, center_y - dialog_height // 2,
                                   dialog_width, dialog_height)
        pygame.draw.rect(screen, (50, 50, 60), dialog_rect, border_radius=8)
        pygame.draw.rect(screen, (180, 160, 120), dialog_rect, 2, border_radius=8)

        # Title
        title_surface = self.menu_font.render(title, True, (220, 200, 160))
        title_rect = title_surface.get_rect(centerx=center_x, centery=center_y - 25)
        screen.blit(title_surface, title_rect)

        # Subtitle
        sub_surface = self.small_font.render(subtitle, True, (180, 140, 100))
        sub_rect = sub_surface.get_rect(centerx=center_x, centery=center_y)
        screen.blit(sub_surface, sub_rect)

        # Hint
        hint_surface = self.small_font.render("[Y] Yes  [N] No", True, (160, 160, 170))
        hint_rect = hint_surface.get_rect(centerx=center_x, centery=center_y + 25)
        screen.blit(hint_surface, hint_rect)
