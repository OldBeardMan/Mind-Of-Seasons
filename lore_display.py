import pygame


def create_placeholder(size, color, name):
    """Create a colored placeholder image with name."""
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill(color)

    # Border
    pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 4)
    pygame.draw.rect(surface, (255, 255, 255), surface.get_rect().inflate(-6, -6), 2)

    # Try to render name if font is available
    try:
        font = pygame.font.Font('Czcionki/PressStart2P.ttf', 8)
        # Split name if too long
        words = name.split()
        y_offset = size[1] // 2 - (len(words) * 10) // 2
        for word in words:
            text = font.render(word, True, (0, 0, 0))
            text_rect = text.get_rect(center=(size[0] // 2, y_offset))
            surface.blit(text, text_rect)
            y_offset += 12
    except:
        pass

    return surface


class LoreDisplay:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # State
        self.is_showing = False
        self.current_item = None
        self.current_page = 0
        self.f_key_pressed = False
        self.cooldown = 0

        # Fonts
        pygame.font.init()
        self.title_font = pygame.font.Font('Czcionki/PressStart2P.ttf', 16)
        self.text_font = pygame.font.Font('Czcionki/PressStart2P.ttf', 10)
        self.hint_font = pygame.font.Font('Czcionki/PressStart2P.ttf', 8)

        # Window dimensions
        self.window_width = 500
        self.window_height = 400
        self.window_x = (screen_width - self.window_width) // 2
        self.window_y = (screen_height - self.window_height) // 2

        # Image size
        self.image_size = (120, 120)

    def show_lore(self, item_data, item_image=None):
        """Start showing lore for an item."""
        self.is_showing = True
        self.current_item = item_data
        self.current_page = 0
        self.f_key_pressed = True  # Prevent immediate skip
        self.cooldown = 15

        # Use provided image or create placeholder
        if item_image:
            self.current_image = pygame.transform.scale(item_image, self.image_size)
        else:
            self.current_image = create_placeholder(
                self.image_size,
                item_data.get("color", (150, 150, 150)),
                item_data.get("name", "???")
            )

    def update(self, keys):
        """Update lore display state. Returns True if still showing."""
        if not self.is_showing:
            return False

        # Cooldown
        if self.cooldown > 0:
            self.cooldown -= 1

        # Handle F key
        if keys[pygame.K_f] and not self.f_key_pressed and self.cooldown == 0:
            self.f_key_pressed = True
            self.current_page += 1
            self.cooldown = 15

            # Check if we've shown all pages
            if self.current_page >= len(self.current_item.get("lore", [])):
                self.is_showing = False
                self.current_item = None
                self.current_page = 0
                return False

        if not keys[pygame.K_f]:
            self.f_key_pressed = False

        return True

    def draw(self, screen):
        """Draw the lore window."""
        if not self.is_showing or not self.current_item:
            return

        # Semi-transparent background overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Main window background
        window_rect = pygame.Rect(self.window_x, self.window_y, self.window_width, self.window_height)
        pygame.draw.rect(screen, (40, 35, 45), window_rect, border_radius=12)
        pygame.draw.rect(screen, (100, 80, 60), window_rect, 4, border_radius=12)
        pygame.draw.rect(screen, (180, 150, 100), window_rect.inflate(-8, -8), 2, border_radius=10)

        # Item image
        image_x = self.window_x + (self.window_width - self.image_size[0]) // 2
        image_y = self.window_y + 30

        # Image frame
        frame_rect = pygame.Rect(image_x - 5, image_y - 5, self.image_size[0] + 10, self.image_size[1] + 10)
        pygame.draw.rect(screen, (60, 50, 40), frame_rect, border_radius=6)
        pygame.draw.rect(screen, (120, 100, 70), frame_rect, 2, border_radius=6)

        screen.blit(self.current_image, (image_x, image_y))

        # Item name
        name = self.current_item.get("name", "Unknown")
        name_surface = self.title_font.render(name, True, (255, 220, 150))
        name_rect = name_surface.get_rect(centerx=self.window_x + self.window_width // 2, top=image_y + self.image_size[1] + 20)
        screen.blit(name_surface, name_rect)

        # Lore text (current page)
        lore_pages = self.current_item.get("lore", [])
        if self.current_page < len(lore_pages):
            lore_text = lore_pages[self.current_page]
            self._draw_wrapped_text(screen, lore_text, name_rect.bottom + 25)

        # Page indicator
        page_text = f"[ {self.current_page + 1} / {len(lore_pages)} ]"
        page_surface = self.hint_font.render(page_text, True, (150, 150, 150))
        page_rect = page_surface.get_rect(centerx=self.window_x + self.window_width // 2, bottom=self.window_y + self.window_height - 45)
        screen.blit(page_surface, page_rect)

        # Continue/close hint
        if self.current_page < len(lore_pages) - 1:
            hint_text = "[F] Continue..."
        else:
            hint_text = "[F] Close"

        hint_surface = self.hint_font.render(hint_text, True, (200, 180, 100))
        hint_rect = hint_surface.get_rect(centerx=self.window_x + self.window_width // 2, bottom=self.window_y + self.window_height - 20)
        screen.blit(hint_surface, hint_rect)

    def _draw_wrapped_text(self, screen, text, start_y):
        """Draw text with word wrapping."""
        max_width = self.window_width - 60
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            test_surface = self.text_font.render(test_line, True, (0, 0, 0))
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())

        # Draw centered lines
        for i, line in enumerate(lines):
            line_surface = self.text_font.render(line, True, (220, 220, 220))
            line_rect = line_surface.get_rect(centerx=self.window_x + self.window_width // 2, top=start_y + i * 18)
            screen.blit(line_surface, line_rect)
