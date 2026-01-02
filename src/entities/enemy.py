import pygame
import random
from src.utils import get_image, get_cached_enemy_spawns, set_cached_enemy_spawns

ENEMY_SIZE = (80, 80)


def load_graphics():
    """Load enemy graphics with animation frames (uses cache)."""
    frames = []
    for i in range(1, 5):
        img = get_image(f'graphics/npc/enemy/enemy{i}.png', ENEMY_SIZE)
        frames.append(img)
    return frames


class Enemy:
    def __init__(self, x, y, tile_size, map_data, tree_tiles=None):
        self.animation_frames = load_graphics()
        self.tile_size = tile_size
        self.map_data = map_data
        # tree_tiles is now passed as a shared set from EnemyManager
        self.tree_tiles = tree_tiles or set()

        # Animation state
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 150  # milliseconds between frames

        # Position in pixels
        self.x = x * tile_size
        self.y = y * tile_size
        # Hitbox smaller than sprite (centered)
        hitbox_w = 40
        hitbox_h = 40
        hitbox_offset_x = (ENEMY_SIZE[0] - hitbox_w) // 2
        hitbox_offset_y = (ENEMY_SIZE[1] - hitbox_h) // 2
        self.hitbox_offset = (hitbox_offset_x, hitbox_offset_y)
        self.rect = pygame.Rect(self.x + hitbox_offset_x, self.y + hitbox_offset_y, hitbox_w, hitbox_h)

        # Movement
        self.speed = 1.5
        self.chase_speed = 2.5  # Szybkość podczas gonienia (wolniejsza niż gracz)
        self.direction = random.choice(['up', 'down', 'left', 'right'])
        self.change_direction_timer = 0
        self.change_direction_interval = random.randint(60, 180)  # frames

        # Chase behavior
        self.is_chasing = False
        self.chase_distance = 150  # pixels - dystans wykrycia gracza
        self.lose_distance = 350  # pixels - dystans utraty gracza

    def _is_walkable(self, tile_x, tile_y):
        """Check if a tile is walkable (path or grass, but not tree)."""
        if 0 <= tile_y < len(self.map_data) and 0 <= tile_x < len(self.map_data[0]):
            # Nie może wchodzić w drzewa
            if (tile_x, tile_y) in self.tree_tiles:
                return False
            # Może chodzić po trawie i ścieżce
            return True
        return False

    def _get_current_tile(self):
        """Get current tile position."""
        return self.rect.centerx // self.tile_size, self.rect.centery // self.tile_size

    def _can_move_to(self, new_rect):
        """Check if enemy can move to new position."""
        # Check all corners of the rect
        corners = [
            (new_rect.left + 10, new_rect.top + 10),
            (new_rect.right - 10, new_rect.top + 10),
            (new_rect.left + 10, new_rect.bottom - 10),
            (new_rect.right - 10, new_rect.bottom - 10),
        ]

        for px, py in corners:
            tile_x = px // self.tile_size
            tile_y = py // self.tile_size
            if not self._is_walkable(tile_x, tile_y):
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

    def _get_distance_to(self, target_rect):
        """Calculate distance to target."""
        dx = target_rect.centerx - self.rect.centerx
        dy = target_rect.centery - self.rect.centery
        return (dx * dx + dy * dy) ** 0.5

    def _get_movement_towards(self, target_rect, speed):
        """Get x,y movement towards target (diagonal movement supported)."""
        dx = target_rect.centerx - self.rect.centerx
        dy = target_rect.centery - self.rect.centery

        # Normalizacja wektora ruchu
        distance = (dx * dx + dy * dy) ** 0.5
        if distance > 0:
            move_x = (dx / distance) * speed
            move_y = (dy / distance) * speed
        else:
            move_x, move_y = 0, 0

        # Ustaw kierunek dla animacji
        if abs(dx) > abs(dy):
            self.direction = 'right' if dx > 0 else 'left'
        else:
            self.direction = 'down' if dy > 0 else 'up'

        return move_x, move_y

    def update(self, dt=16, player_rect=None):
        """Update enemy position, AI and animation."""
        self.change_direction_timer += 1

        # Update animation
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)

        # Check if should chase player
        if player_rect:
            distance = self._get_distance_to(player_rect)

            if distance < self.chase_distance:
                self.is_chasing = True
            elif distance > self.lose_distance:
                self.is_chasing = False

        if self.is_chasing and player_rect:
            # Ruch po przekątnej w kierunku gracza
            move_x, move_y = self._get_movement_towards(player_rect, self.chase_speed)

            new_rect = self.rect.copy()
            new_rect.x += move_x
            new_rect.y += move_y

            # Spróbuj ruchu pełnego
            if self._can_move_to(new_rect):
                self.rect = new_rect
                self.x = self.rect.x - self.hitbox_offset[0]
                self.y = self.rect.y - self.hitbox_offset[1]
            else:
                # Spróbuj ruchu tylko w X
                new_rect_x = self.rect.copy()
                new_rect_x.x += move_x
                if self._can_move_to(new_rect_x):
                    self.rect = new_rect_x
                    self.x = self.rect.x - self.hitbox_offset[0]
                    self.y = self.rect.y - self.hitbox_offset[1]
                else:
                    # Spróbuj ruchu tylko w Y
                    new_rect_y = self.rect.copy()
                    new_rect_y.y += move_y
                    if self._can_move_to(new_rect_y):
                        self.rect = new_rect_y
                        self.x = self.rect.x - self.hitbox_offset[0]
                        self.y = self.rect.y - self.hitbox_offset[1]
        else:
            # Random direction change when not chasing
            if self.change_direction_timer >= self.change_direction_interval:
                self.change_direction_timer = 0
                self.change_direction_interval = random.randint(30, 120)
                self.direction = self._choose_new_direction()

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

            # Move if possible
            if self._can_move_to(new_rect):
                self.rect = new_rect
                self.x = self.rect.x - self.hitbox_offset[0]
                self.y = self.rect.y - self.hitbox_offset[1]

    def check_collision(self, player_rect):
        """Check collision with player."""
        return self.rect.colliderect(player_rect)

    def draw(self, screen, camera_offset):
        """Draw enemy with camera offset."""
        # Draw sprite at visual position (not hitbox position)
        screen_pos = (self.x - camera_offset[0],
                      self.y - camera_offset[1])

        # Get current animation frame
        img = self.animation_frames[self.current_frame]

        # Flip sprite based on direction
        if self.direction == 'left':
            img = pygame.transform.flip(img, True, False)

        screen.blit(img, screen_pos)


class EnemyManager:
    """Manages all enemies in the game."""

    def __init__(self, tile_size, map_data, spawn_point, tree_positions=None, num_enemies=10):
        self.tile_size = tile_size
        self.map_data = map_data
        self.tree_positions = tree_positions or []
        self.tree_tiles = set((tx, ty) for tx, ty, _ in self.tree_positions)
        self.enemies = []

        # Try to use cached spawn positions (huge performance gain on respawn)
        cache_key = (len(map_data), len(map_data[0]) if map_data else 0, spawn_point, num_enemies)
        cached_positions = get_cached_enemy_spawns(cache_key)

        if cached_positions:
            spawn_positions = cached_positions
        else:
            spawn_positions = self._find_spawn_positions(spawn_point, num_enemies)
            set_cached_enemy_spawns(cache_key, spawn_positions)

        # Create enemies with shared tree_tiles set (huge performance gain)
        for pos in spawn_positions:
            enemy = Enemy(pos[0], pos[1], tile_size, map_data, self.tree_tiles)
            self.enemies.append(enemy)

    def _is_near_tree(self, x, y, radius=2):
        """Check if position is near any tree (trees are larger than 1 tile)."""
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if (x + dx, y + dy) in self.tree_tiles:
                    return True
        return False

    def _find_spawn_positions(self, spawn_point, num_enemies):
        """Find valid spawn positions on paths only, away from player spawn."""
        valid_positions = []
        min_distance_from_spawn = 25  # tiles - safe zone around cabin

        for y in range(len(self.map_data)):
            for x in range(len(self.map_data[y])):
                # Spawn only on paths (not grass between trees)
                if self.map_data[y][x] != 'path':
                    continue

                # Check distance from spawn
                dist = ((x - spawn_point[0]) ** 2 + (y - spawn_point[1]) ** 2) ** 0.5
                if dist > min_distance_from_spawn:
                    valid_positions.append((x, y))

        # Select random positions, ensuring some spacing
        selected = []
        min_enemy_spacing = 8  # tiles between enemies

        random.shuffle(valid_positions)
        for pos in valid_positions:
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

    def update(self, dt=16, player_rect=None):
        """Update all enemies."""
        for enemy in self.enemies:
            enemy.update(dt, player_rect)

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
