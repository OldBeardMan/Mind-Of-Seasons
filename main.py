import pygame

"""
TODO Lista rzeczy do zrobienia:
====================================
1. [x] Kolizje z drzewami - DONE
2. [x] Kotki spawnują się tylko w dostępnych miejscach (nie na drzewach) - DONE
3. [ ] System dialogu ze Sprytkiem:
       - Wyświetlanie tekstu w dymku
       - Możliwość interakcji (klawisz np. F)
       - Różne dialogi/questy
4. [ ] Zbieranie kotków do ekwipunku:
       - Podejście do kotka + klawisz interakcji
       - Kotki znikają z mapy po zebraniu
       - Wyświetlanie zebranych kotków w inventory
5. [ ] Baza/Domek gracza:
       - Grafika domku na mapie
       - Strefa oddawania kotków
       - Licznik zebranych kotków
6. [ ] UI ekwipunku:
       - Sloty na kotki
       - Podgląd zebranych kotków
====================================
"""

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
    player.update(keys, clock, npc, background)

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

