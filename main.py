import pygame
from player import Player
from background import Background

# Inicjalizacja Pygame i ustawienia ekranu
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()
clock = pygame.time.Clock()

# Tworzenie instancji gracza i tła
player = Player(screen_width, screen_height)
background = Background(screen_width, screen_height)

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
    player.update(keys, clock)
    
    # Rysowanie tła, gracza i liści
    background.draw_tiles(screen)
    player.draw(screen)
    background.draw_leaves(screen)
    
    # Aktualizacja ekranu
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

