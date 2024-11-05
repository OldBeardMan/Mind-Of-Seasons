import pygame
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
background = Background(map_width, map_height, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT)
player = Player(SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE)
inventory=Inventory(SCREEN_WIDTH, SCREEN_HEIGHT)
npc=Npc(SCREEN_WIDTH, SCREEN_HEIGHT, x=300, y=400)

# Główna pętla gry
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    keys = pygame.key.get_pressed()

    # Aktualizacja gracza
    player.update(keys, clock,npc)

    # Oblicz przesunięcie kamery
    camera_offset = calculate_camera_offset(player, map_width, map_height, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT)

    # Rysowanie tła, gracza i liści i inventory i sprytka
    background.draw(screen, camera_offset, player)
    npc.draw_sprytek(screen, camera_offset)
    background.draw_leaves(screen, camera_offset)
    inventory.update_inventory(keys, screen)

    npc.draw_chat_graphics(screen,player, camera_offset)

    # Aktualizacja ekranu
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

