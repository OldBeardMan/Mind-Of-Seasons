import pygame

# Inicjalizacja Pygame
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # pełnoekranowy tryb
screen_width, screen_height = screen.get_size()
clock = pygame.time.Clock()

#GRACZ
# Załadowanie grafik i skalowanie
image_idle = pygame.image.load('Grafiki/Character/character_idle.png').convert_alpha()
image_walk1 = pygame.image.load('Grafiki/Character/character_walk1.png').convert_alpha()
image_walk2 = pygame.image.load('Grafiki/Character/character_walk2.png').convert_alpha()

# Skalowanie obrazków do mniejszych rozmiarów (np. 50x50)
scale_size = (70, 70)
image_idle = pygame.transform.scale(image_idle, scale_size)
image_walk1 = pygame.transform.scale(image_walk1, scale_size)
image_walk2 = pygame.transform.scale(image_walk2, scale_size)

# Przechowywanie animacji w liście
walk_animation = [image_walk1, image_walk2]
current_frame = 0
animation_timer = 0
animation_speed = 200  # czas w milisekundach między klatkami

# Ustawienia postaci
player_rect = image_idle.get_rect(center=(screen_width // 2, screen_height // 2))
speed = 5  # zwiększona prędkość ruchu
is_walking = False
facing_right = False # aby określić, czy postać jest skierowana w prawo

#TŁO
# Załadowanie obrazka kafelka
tile_image = pygame.image.load('Grafiki/Landscape/kafelek.png').convert_alpha()

# Ustawienia kafelków
tile_size = 64  # Rozmiar kafelka, np. 64x64 pikseli
tile_image = pygame.transform.scale(tile_image, (tile_size, tile_size))

# Generowanie siatki kafelków na tle
def draw_tiles():
    for y in range(0, screen_height, tile_size):
        for x in range(0, screen_width, tile_size):
            screen.blit(tile_image, (x, y))


#LIŚCIE
# Załadowanie obrazka liści
leaves_img0 = pygame.image.load('Grafiki/Landscape/Leaves/0.png').convert_alpha()
leaves_img1 = pygame.image.load('Grafiki/Landscape/Leaves/1.png').convert_alpha()
leaves_img2 = pygame.image.load('Grafiki/Landscape/Leaves/2.png').convert_alpha()
leaves_img3 = pygame.image.load('Grafiki/Landscape/Leaves/3.png').convert_alpha()
leaves_img4 = pygame.image.load('Grafiki/Landscape/Leaves/4.png').convert_alpha()

# Ustawienia liści
leaves_size = 128  # Rozmiar liści kuan dupan
leaves_img0 = pygame.transform.scale(leaves_img0, (leaves_size, leaves_size))
leaves_img1 = pygame.transform.scale(leaves_img1, (leaves_size, leaves_size))
leaves_img2 = pygame.transform.scale(leaves_img2, (leaves_size, leaves_size))
leaves_img3 = pygame.transform.scale(leaves_img3, (leaves_size, leaves_size))
leaves_img4 = pygame.transform.scale(leaves_img4, (leaves_size, leaves_size))

# Przechowywanie animacji w liście
leaves_animation = [leaves_img0, leaves_img1, leaves_img2, leaves_img3, leaves_img4]
l_frame = 0
l_timer = 0
l_speed = 200  # czas w milisekundach między klatkami

# Generowanie liści w grze
def draw_leaves():
    global l_frame, l_timer
    current_time = pygame.time.get_ticks()  # Czas w milisekundach

    # Sprawdzanie, czy nadszedł czas na przełączenie klatki animacji
    if current_time - l_timer > l_speed:
        l_frame = (l_frame + 1) % len(leaves_animation)  # Przełącz klatkę animacji
        l_timer = current_time  # Zresetuj timer

    for y in range(0, screen_height, leaves_size):
        for x in range(0, screen_width, leaves_size):
            screen.blit(leaves_animation[l_frame], (x, y))  # Wyświetl bieżącą klatkę animacji

# Główna pętla gry
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False  # Dodane, aby wyjść z gry po wciśnięciu ESC

    keys = pygame.key.get_pressed()
    is_walking = False

    # Ruch postaci
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player_rect.x += speed
        is_walking = True
        facing_right = True  # skierowany w prawo

    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player_rect.x -= speed
        is_walking = True
        facing_right = False  # skierowany w lewo

    if keys[pygame.K_w] or keys[pygame.K_UP]:
        player_rect.y -= speed
        is_walking = True

    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        player_rect.y += speed
        is_walking = True

    # Animacja chodzenia
    if is_walking:
        animation_timer += clock.get_time()
        if animation_timer > animation_speed:
            animation_timer = 0
            current_frame = (current_frame + 1) % len(walk_animation)
        player_image = walk_animation[current_frame]
    else:
        player_image = image_idle

    # Obracanie obrazka postaci w zależności od kierunku
    if facing_right:
        player_image = pygame.transform.flip(player_image, True, False)

    # Rysowanie i aktualizacja ekranu
    draw_tiles()
    screen.blit(player_image, player_rect)
    draw_leaves()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()


