import pygame
# TODO zaprogramować kamerę, aby podążała za graczem
# TODO aktualnie w sterowaniu graczem sprawdzana jest kolizja tylko ze sprytkiem , jeśli chcemy sprawdzić kolizje z wieoma obiektami trzeba zrobić tablice obiektów
# Funkcja do ładowania i skalowania grafiki gracza
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

# Klasa Gracza
class Player:
    def __init__(self, screen_width, screen_height):
        self.image = None
        self.image_idle, self.walk_animation = load_player_graphics()
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 200
        self.speed = 5
        self.is_walking = False
        self.facing_right = True
        self.player_rect = self.image_idle.get_rect(center=(screen_width // 2, screen_height // 2))
        
    def update(self, keys, clock,npc):
        self.is_walking = False
        #kopia pozycji gracza do sprawdzenia kolizji
        new_position = self.player_rect.copy()
        # Ruch w poziomie
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            new_position.x += self.speed
            self.is_walking = True
            self.facing_right = True
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            new_position.x -= self.speed
            self.is_walking = True
            self.facing_right = False

        # Sprawdzenie kolizji w poziomie ze sprytkiem
        if not new_position.colliderect(npc.sprytek_rect):
            self.player_rect.x = new_position.x  # Aktualizacja pozycji poziomej tylko, gdy nie ma kolizji

        # Ruch w pionie
        new_position = self.player_rect.copy()  # Ponownie kopiujemy pozycję, aby sprawdzić ruch pionowy
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            new_position.y -= self.speed
            self.is_walking = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            new_position.y += self.speed
            self.is_walking = True

        # Sprawdzenie kolizji w pionie ze sprytkiem
        if not new_position.colliderect(npc.sprytek_rect):
            self.player_rect.y = new_position.y  # Aktualizacja pozycji pionowej tylko, gdy nie ma kolizji

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
        
    def draw(self, screen):
        screen.blit(self.image, self.player_rect)
