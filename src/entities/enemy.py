import pygame
import random

ENEMY_SIZE = (50, 50)


def load_graphics():
    """Load enemy graphics - reuse cat sprites with tint."""
    # Use a cat sprite as base and tint it red to make it look hostile
    enemy_img = pygame.image.load('Grafiki/NPC/Cat2.png').convert_alpha()
    enemy_img = pygame.transform.scale(enemy_img, ENEMY_SIZE)

    # Create red tint for hostile appearance
    tinted = enemy_img.copy()
    tinted.fill((255, 100, 100), special_flags=pygame.BLEND_RGB_MULT)

    return tinted


class Enemy:
    def __init__(self, x, y, tile_size, map_data):
        self.image = load_graphics()
        self.tile_size = tile_size
        self.map_data = map_data

        # Position in pixels
        self.x = x * tile_size
        self.y = y * tile_size
        self.rect = pygame.Rect(self.x, self.y, ENEMY_SIZE[0], ENEMY_SIZE[1])

        # Movement
        self.speed = 2
        self.direction = random.choice(['up', 'down', 'left', 'right'])
        self.change_direction_timer = 0
        self.change_direction_interval = random.randint(60, 180)  # frames

    def _is_path(self, tile_x, tile_y):
        """Check if a tile is a path."""
        if 0 <= tile_y < len(self.map_data) and 0 <= tile_x < len(self.map_data[0]):
            return self.map_data[tile_y][tile_x] == 'path'
        return False

    def _get_current_tile(self):
        """Get current tile position."""
        return self.rect.centerx // self.tile_size, self.rect.centery // self.tile_size

    def _can_move_to(self, new_rect):
        """Check if enemy can move to new position (stays on path)."""
        # Check all corners of the rect
        corners = [
            (new_rect.left, new_rect.top),
            (new_rect.right - 1, new_rect.top),
            (new_rect.left, new_rect.bottom - 1),
            (new_rect.right - 1, new_rect.bottom - 1),
        ]

        for px, py in corners:
            tile_x = px // self.tile_size
            tile_y = py // self.tile_size
            if not self._is_path(tile_x, tile_y):
                return False
        return True

    def _choose_new_direction(self):
        """Choose a new valid direction to move."""
        directions = ['up', 'down', 'left', 'right']
        random.shuffle(directions)

        for direction in directions:
            test_rect = self.rect.copy()
            if direction == 'up':
                test_rect.y -= self.speed * 2
            elif direction == 'down':
                test_rect.y += self.speed * 2
            elif direction == 'left':
                test_rect.x -= self.speed * 2
            elif direction == 'right':
                test_rect.x += self.speed * 2

            if self._can_move_to(test_rect):
                return direction

        return self.direction  # Keep current if no valid direction

    def update(self):
        """Update enemy position and AI."""
        self.change_direction_timer += 1

        # Change direction at random intervals
        if self.change_direction_timer >= self.change_direction_interval:
            self.change_direction_timer = 0
            self.change_direction_interval = random.randint(30, 120)
            self.direction = random.choice(['up', 'down', 'left', 'right'])

        # Try to move in current direction
        new_rect = self.rect.copy()
        if self.direction == 'up':
            new_rect.y -= self.speed
        elif self.direction == 'down':
            new_rect.y += self.speed
        elif self.direction == 'left':
            new_rect.x -= self.speed
        elif self.direction == 'right':
            new_rect.x += self.speed

        # Move if possible (stay on path)
        if self._can_move_to(new_rect):
            self.rect = new_rect
            self.x = self.rect.x
            self.y = self.rect.y

    def check_collision(self, player_rect):
        """Check collision with player."""
        return self.rect.colliderect(player_rect)

    def draw(self, screen, camera_offset):
        """Draw enemy with camera offset."""
        screen_pos = (self.rect.x - camera_offset[0],
                      self.rect.y - camera_offset[1])

        # Flip sprite based on direction
        img = self.image
        if self.direction == 'left':
            img = pygame.transform.flip(self.image, True, False)

        screen.blit(img, screen_pos)


class EnemyManager:
    """Manages all enemies in the game."""

    def __init__(self, tile_size, map_data, spawn_point, num_enemies=10):
        self.tile_size = tile_size
        self.map_data = map_data
        self.enemies = []

        # Find path positions for spawning (excluding area near spawn)
        spawn_positions = self._find_spawn_positions(spawn_point, num_enemies)

        for pos in spawn_positions:
            enemy = Enemy(pos[0], pos[1], tile_size, map_data)
            self.enemies.append(enemy)

    def _find_spawn_positions(self, spawn_point, num_enemies):
        """Find valid spawn positions on paths, away from player spawn."""
        path_positions = []
        min_distance_from_spawn = 15  # tiles

        for y in range(len(self.map_data)):
            for x in range(len(self.map_data[y])):
                if self.map_data[y][x] == 'path':
                    # Check distance from spawn
                    dist = ((x - spawn_point[0]) ** 2 + (y - spawn_point[1]) ** 2) ** 0.5
                    if dist > min_distance_from_spawn:
                        path_positions.append((x, y))

        # Select random positions, ensuring some spacing
        selected = []
        min_enemy_spacing = 8  # tiles between enemies

        random.shuffle(path_positions)
        for pos in path_positions:
            if len(selected) >= num_enemies:
                break

            # Check spacing from other enemies
            too_close = False
            for other in selected:
                dist = ((pos[0] - other[0]) ** 2 + (pos[1] - other[1]) ** 2) ** 0.5
                if dist < min_enemy_spacing:
                    too_close = True
                    break

            if not too_close:
                selected.append(pos)

        return selected

    def update(self):
        """Update all enemies."""
        for enemy in self.enemies:
            enemy.update()

    def check_player_collision(self, player_rect):
        """Check if player collides with any enemy."""
        for enemy in self.enemies:
            if enemy.check_collision(player_rect):
                return True
        return False

    def draw(self, screen, camera_offset):
        """Draw all enemies."""
        for enemy in self.enemies:
            enemy.draw(screen, camera_offset)
