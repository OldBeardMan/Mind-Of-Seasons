import pygame
from map_generator import map_initialization
from player import Player
from background import Background
from camera import calculate_camera_offset
from inventory import Inventory
from npc import Npc

# Inicjalizacja Pygame i ustawienia ekranu
pygame.init()
TILE_SIZE = 64
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
clock = pygame.time.Clock()
pygame.display.set_caption("Swędząca dupa xddddd")

# Tworzenie instancji gracza i tła
map_width, map_height = 50, 50  # Większa mapa niż ekran
map_initialization(map_width, map_height)
background = Background(map_width, map_height, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT)
player = Player(SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE)
inventory=Inventory(SCREEN_WIDTH, SCREEN_HEIGHT)
npc=Npc(SCREEN_WIDTH, SCREEN_HEIGHT, x=300, y=400)

# Cooldown zbierania kotków
collect_cooldown = 0
f_key_was_pressed = False

# Główna pętla gry
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    keys = pygame.key.get_pressed()

    # Aktualizacja gracza i NPC
    player.update(keys, clock, npc, background)
    npc.update(keys, player)

    # Obsługa cooldownu zbierania
    if collect_cooldown > 0:
        collect_cooldown -= 1

    # Sprawdź bliskość kotka i obsłuż zbieranie
    cat_index, cat_image_index = background.check_cat_proximity(player.player_rect)
    if cat_index is not None:
        inventory.set_collect_hint(True)
        # Zbieranie kotka klawiszem F (tylko gdy nie rozmawiamy z NPC i cooldown minął)
        if keys[pygame.K_f] and not f_key_was_pressed and not npc.is_talking and collect_cooldown == 0:
            collected = background.collect_cat(cat_index)
            if collected:
                inventory.add_cat(cat_image_index)
                collect_cooldown = 30  # Cooldown przed następnym zbieraniem
    else:
        inventory.set_collect_hint(False)

    # Śledzenie stanu klawisza F dla zbierania
    f_key_was_pressed = keys[pygame.K_f]

    # Oblicz przesunięcie kamery
    camera_offset = calculate_camera_offset(player, map_width, map_height, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT)

    # Rysowanie tła, gracza i liści i inventory i sprytka
    background.draw(screen, camera_offset, player)
    npc.draw_sprytek(screen, camera_offset)
    background.draw_leaves(screen, camera_offset)
    inventory.update_inventory(keys, screen)

    npc.draw_chat_graphics(screen, player, camera_offset)

    # Aktualizacja ekranu
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

