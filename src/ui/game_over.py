import pygame
from src.utils import get_font, get_image


class GameOverScreen:
    """Game over screen with death reason and restart option."""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_showing = False
        self.death_reason = ""
        self.cooldown = 0

        # Fonts
        self.title_font = get_font(32)
        self.reason_font = get_font(14)
        self.hint_font = get_font(10)
        self.zzz_font = get_font(24)

        # Enemy animation frames
        self.enemy_frames = []
        for i in range(1, 5):
            img = get_image(f'graphics/npc/enemy/enemy{i}.png', (100, 100))
            if img:
                self.enemy_frames.append(img)

        # Animation state
        self.anim_timer = 0
        self.current_frame = 0

    def show(self, reason):
        """Show game over screen with given reason."""
        self.is_showing = True
        self.death_reason = reason
        self.cooldown = 60  # 1 second delay before allowing restart
        self.anim_timer = 0

    def update(self, keys):
        """Update game over screen. Returns 'restart' if player wants to restart."""
        if not self.is_showing:
            return None

        self.anim_timer += 1

        # Animate enemy (every 10 frames)
        if self.anim_timer % 10 == 0 and self.enemy_frames:
            self.current_frame = (self.current_frame + 1) % len(self.enemy_frames)

        # Cooldown before allowing restart
        if self.cooldown > 0:
            self.cooldown -= 1
            return None

        # Check for restart input
        if keys[pygame.K_SPACE] or keys[pygame.K_f]:
            self.is_showing = False
            self.death_reason = ""
            return "restart"

        return None

    def draw(self, screen):
        """Draw the game over screen."""
        if not self.is_showing:
            return

        # Dark overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        # "GAME OVER" title
        title_surface = self.title_font.render("GAME OVER", True, (255, 80, 80))
        title_rect = title_surface.get_rect(centerx=center_x, centery=center_y - 80)
        screen.blit(title_surface, title_rect)

        # Death reason
        reason_surface = self.reason_font.render(self.death_reason, True, (220, 220, 220))
        reason_rect = reason_surface.get_rect(centerx=center_x, centery=center_y - 30)
        screen.blit(reason_surface, reason_rect)

        # Draw graphic based on death type
        if "asleep" in self.death_reason.lower():
            self._draw_zzz_animation(screen, center_x, center_y + 30)
        else:
            # Enemy graphic with animation and background
            if self.enemy_frames:
                # Light background circle so enemy is visible
                pygame.draw.circle(screen, (60, 50, 70), (center_x, center_y + 40), 60)
                pygame.draw.circle(screen, (80, 70, 90), (center_x, center_y + 40), 55)

                # Draw animated enemy
                enemy_img = self.enemy_frames[self.current_frame]
                img_rect = enemy_img.get_rect(centerx=center_x, centery=center_y + 40)
                screen.blit(enemy_img, img_rect)

        # Restart hint
        if self.cooldown <= 0:
            hint_surface = self.hint_font.render("[SPACE] Try Again", True, (200, 180, 100))
        else:
            hint_surface = self.hint_font.render("...", True, (150, 150, 150))

        hint_rect = hint_surface.get_rect(centerx=center_x, centery=center_y + 120)
        screen.blit(hint_surface, hint_rect)

    def _draw_zzz_animation(self, screen, center_x, center_y):
        """Draw floating ZZZ animation."""
        for i, char in enumerate("ZZZ"):
            # Each Z floats up and down with offset timing
            offset = (self.anim_timer + i * 20) % 60
            float_y = abs(offset - 30) / 30 * 10

            x = center_x - 40 + i * 30
            y = center_y - float_y + i * 10

            # Shadow
            shadow = self.zzz_font.render(char, True, (50, 50, 80))
            screen.blit(shadow, (x + 2, y + 2))

            # Letter
            letter = self.zzz_font.render(char, True, (150, 150, 255))
            screen.blit(letter, (x, y))
