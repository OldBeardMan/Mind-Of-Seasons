import pygame

def load_player_graphics():
    image_idle = pygame.image.load('Grafiki/Character/character_idle.png').convert_alpha()
    image_walk1 = pygame.image.load('Grafiki/Character/character_walk1.png').convert_alpha()
    image_walk2 = pygame.image.load('Grafiki/Character/character_walk2.png').convert_alpha()
    
    scale_size = (70, 70)
    image_idle = pygame.transform.scale(image_idle, scale_size)
    image_walk1 = pygame.transform.scale(image_walk1, scale_size)
    image_walk2 = pygame.transform.scale(image_walk2, scale_size)
    
    walk_animation = [image_walk1, image_walk2]
    return image_idle, walk_animation

class Player:
    def __init__(self, screen_width, screen_height, tile_size):
        self.image = None
        self.image_idle, self.walk_animation = load_player_graphics()
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 200
        self.speed = 5
        self.is_walking = False
        self.facing_right = True
        self.tile_size = tile_size
        self.map_position = [10, 10]  # Pozycja gracza na mapie (w kafelkach)
        self.player_rect = self.image_idle.get_rect(center=(screen_width // 2, screen_height // 2))
        
    def update(self, keys, clock, npc, background=None):
        self.is_walking = False
        new_position = self.player_rect.copy()

        # Ruch poziomy
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            new_position.x += self.speed
            self.is_walking = True
            self.facing_right = True
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            new_position.x -= self.speed
            self.is_walking = True
            self.facing_right = False

        # Kolizja ze sprytkiem i drzewami w poziomie
        can_move_x = not new_position.colliderect(npc.sprytek_rect)
        if can_move_x and background:
            can_move_x = not background.check_tree_collision(new_position)
        if can_move_x:
            self.player_rect.x = new_position.x

        # Ruch pionowy
        new_position = self.player_rect.copy()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            new_position.y -= self.speed
            self.is_walking = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            new_position.y += self.speed
            self.is_walking = True

        # Kolizja ze sprytkiem i drzewami w pionie
        can_move_y = not new_position.colliderect(npc.sprytek_rect)
        if can_move_y and background:
            can_move_y = not background.check_tree_collision(new_position)
        if can_move_y:
            self.player_rect.y = new_position.y

        # Aktualizacja pozycji gracza na mapie (w kafelkach)
        self.map_position[0] = self.player_rect.x // self.tile_size
        self.map_position[1] = self.player_rect.y // self.tile_size

        # Animacja chodzenia
        if self.is_walking:
            self.animation_timer += clock.get_time()
            if self.animation_timer > self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.walk_animation)
            self.image = self.walk_animation[self.current_frame]
        else:
            self.image = self.image_idle

        # Obracanie w prawo/lewo
        if self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
        
    def draw(self, screen, camera_offset):
        # Rysowanie z przesunięciem kamery
        screen_x = self.player_rect.x - camera_offset[0]
        screen_y = self.player_rect.y - camera_offset[1]
        screen.blit(self.image, (screen_x, screen_y))
