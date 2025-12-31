import pygame
from src.utils import get_image

PLAYER_SIZE = (70, 70)


def load_graphics():
    """Load and scale player graphics (uses cache)."""
    idle = get_image('graphics/character/character_idle.png', PLAYER_SIZE)
    walk1 = get_image('graphics/character/character_walk1.png', PLAYER_SIZE)
    walk2 = get_image('graphics/character/character_walk2.png', PLAYER_SIZE)

    return idle, [walk1, walk2]


class Player:
    def __init__(self, screen_width, screen_height, tile_size, spawn_position=None):
        self.idle_image, self.walk_animation = load_graphics()
        self.image = self.idle_image
        self.tile_size = tile_size

        # Animation state
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 200

        # Movement state
        self.base_speed = 5
        self.speed = self.base_speed
        self.is_walking = False
        self.facing_right = True

        # Fatigue system
        self.fatigue = 100.0  # 0-100 scale (100 = fully awake)
        self.fatigue_decay = 0.0093  # per frame (~3 min to empty at 60fps)

        # Position
        if spawn_position:
            spawn_x = spawn_position[0] * tile_size
            spawn_y = spawn_position[1] * tile_size
            self.map_position = list(spawn_position)
            self.player_rect = self.idle_image.get_rect(topleft=(spawn_x, spawn_y))
        else:
            self.map_position = [10, 10]
            self.player_rect = self.idle_image.get_rect(center=(screen_width // 2, screen_height // 2))

    def update(self, keys, clock, npc, background=None, cabin=None):
        """Update player position and animation."""
        self.is_walking = False

        # Horizontal movement
        new_pos = self.player_rect.copy()
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            new_pos.x += self.speed
            self.is_walking = True
            self.facing_right = True
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            new_pos.x -= self.speed
            self.is_walking = True
            self.facing_right = False

        # Horizontal collision check
        can_move = not new_pos.colliderect(npc.sprytek_rect)
        if can_move and background:
            can_move = not background.check_tree_collision(new_pos)
        if can_move and cabin:
            can_move = not cabin.check_collision(new_pos)
        if can_move:
            self.player_rect.x = new_pos.x

        # Vertical movement
        new_pos = self.player_rect.copy()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            new_pos.y -= self.speed
            self.is_walking = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            new_pos.y += self.speed
            self.is_walking = True

        # Vertical collision check
        can_move = not new_pos.colliderect(npc.sprytek_rect)
        if can_move and background:
            can_move = not background.check_tree_collision(new_pos)
        if can_move and cabin:
            can_move = not cabin.check_collision(new_pos)
        if can_move:
            self.player_rect.y = new_pos.y

        # Update map position (in tiles)
        self.map_position[0] = self.player_rect.x // self.tile_size
        self.map_position[1] = self.player_rect.y // self.tile_size

        # Animation
        if self.is_walking:
            self.animation_timer += clock.get_time()
            if self.animation_timer > self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.walk_animation)
            self.image = self.walk_animation[self.current_frame]
        else:
            self.image = self.idle_image

        # Flip sprite based on direction
        if self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def draw(self, screen, camera_offset):
        """Draw player with camera offset."""
        screen_pos = (self.player_rect.x - camera_offset[0],
                      self.player_rect.y - camera_offset[1])
        screen.blit(self.image, screen_pos)

    def update_fatigue(self, dt):
        """Update fatigue level (decreases over time)."""
        self.fatigue -= self.fatigue_decay
        if self.fatigue < 0:
            self.fatigue = 0

        # Update speed based on fatigue
        if self.fatigue < 30:
            # Linear slowdown from 100% to 40% speed as fatigue goes 30 -> 0
            fatigue_factor = max(0.4, self.fatigue / 30)
            self.speed = self.base_speed * fatigue_factor
        else:
            self.speed = self.base_speed

    def drink_coffee(self):
        """Restore fatigue to full."""
        self.fatigue = 100.0
        self.speed = self.base_speed

    def get_fatigue_percent(self):
        """Get current fatigue as percentage (0-100)."""
        return self.fatigue

    def is_exhausted(self):
        """Check if player is completely exhausted."""
        return self.fatigue <= 0
