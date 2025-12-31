"""Loading screen for Mind of Seasons."""

import pygame
from src.utils import get_font


class LoadingScreen:
    """Loading screen displayed during game startup and loading."""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Fonts
        self.title_font = get_font(32)
        self.loading_font = get_font(14)

        # Animation
        self.dots = 0
        self.dot_timer = 0
        self.dot_speed = 30  # frames between dot changes

        # Progress (optional)
        self.progress = 0
        self.progress_text = "Loading..."

    def set_progress(self, progress, text=None):
        """Set loading progress (0-100) and optional text."""
        self.progress = max(0, min(100, progress))
        if text:
            self.progress_text = text

    def update(self):
        """Update loading animation."""
        self.dot_timer += 1
        if self.dot_timer >= self.dot_speed:
            self.dot_timer = 0
            self.dots = (self.dots + 1) % 4

    def draw(self, screen):
        """Draw the loading screen."""
        # Dark background
        screen.fill((20, 20, 30))

        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        # Title
        title_surface = self.title_font.render("MIND OF SEASONS", True, (200, 180, 140))
        title_rect = title_surface.get_rect(centerx=center_x, centery=center_y - 60)
        screen.blit(title_surface, title_rect)

        # Loading text with animated dots
        dots_text = "." * self.dots
        loading_text = f"{self.progress_text}{dots_text}"
        loading_surface = self.loading_font.render(loading_text, True, (150, 150, 160))
        loading_rect = loading_surface.get_rect(centerx=center_x, centery=center_y + 20)
        screen.blit(loading_surface, loading_rect)

        # Progress bar (if progress is set)
        if self.progress > 0:
            bar_width = 200
            bar_height = 8
            bar_x = center_x - bar_width // 2
            bar_y = center_y + 50

            # Background bar
            pygame.draw.rect(screen, (60, 60, 70), (bar_x, bar_y, bar_width, bar_height), border_radius=4)

            # Progress fill
            fill_width = int(bar_width * self.progress / 100)
            if fill_width > 0:
                pygame.draw.rect(screen, (180, 150, 100), (bar_x, bar_y, fill_width, bar_height), border_radius=4)
