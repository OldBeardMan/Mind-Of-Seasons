import pygame
from map_generator import map_initialization
from player import Player
from background import Background
from camera import calculate_camera_offset
from inventory import Inventory
from npc import Npc
from enemy import EnemyManager

# Initialize Pygame
pygame.init()
TILE_SIZE = 64
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
clock = pygame.time.Clock()
pygame.display.set_caption("Mind of Seasons")


def init_game():
    """Initialize or restart the game."""
    # Initialize map and get cat/spawn positions
    MAP_WIDTH, MAP_HEIGHT = 1000, 1000
    cat_positions, spawn_point = map_initialization(MAP_WIDTH, MAP_HEIGHT, num_cats=50)

    # Fallback values if map data is missing
    if spawn_point is None:
        spawn_point = (MAP_WIDTH // 2, MAP_HEIGHT // 2)
    if not cat_positions:
        cat_positions = []

    # Create game objects
    background = Background(MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, cat_positions)
    player = Player(SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, spawn_position=spawn_point)
    inventory = Inventory(SCREEN_WIDTH, SCREEN_HEIGHT)

    # NPC spawns near player
    npc_x = (spawn_point[0] + 3) * TILE_SIZE
    npc_y = (spawn_point[1] + 2) * TILE_SIZE
    npc = Npc(SCREEN_WIDTH, SCREEN_HEIGHT, x=npc_x, y=npc_y)

    # Enemies spawn on paths
    enemy_manager = EnemyManager(TILE_SIZE, background.map_data, spawn_point, num_enemies=20)

    return background, player, inventory, npc, enemy_manager, spawn_point, MAP_WIDTH, MAP_HEIGHT


# Initialize game
background, player, inventory, npc, enemy_manager, spawn_point, MAP_WIDTH, MAP_HEIGHT = init_game()

# Cat collection state
collect_cooldown = 0
f_key_pressed = False

# Main game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    keys = pygame.key.get_pressed()

    # Update game objects
    player.update(keys, clock, npc, background)
    npc.update(keys, player)
    enemy_manager.update()

    # Check enemy collision - restart game if hit
    if enemy_manager.check_player_collision(player.player_rect):
        background, player, inventory, npc, enemy_manager, spawn_point, MAP_WIDTH, MAP_HEIGHT = init_game()
        collect_cooldown = 0
        f_key_pressed = False
        continue

    # Cat collection cooldown
    if collect_cooldown > 0:
        collect_cooldown -= 1

    # Check cat proximity and handle collection
    cat_index, cat_image_index = background.check_cat_proximity(player.player_rect)
    if cat_index is not None:
        inventory.set_collect_hint(True)
        # Collect cat with F key (not during NPC dialogue, with cooldown)
        if keys[pygame.K_f] and not f_key_pressed and not npc.is_talking and collect_cooldown == 0:
            collected = background.collect_cat(cat_index)
            if collected:
                inventory.add_cat(cat_image_index)
                collect_cooldown = 30
    else:
        inventory.set_collect_hint(False)

    f_key_pressed = keys[pygame.K_f]

    # Calculate camera offset
    camera_offset = calculate_camera_offset(player, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT)

    # Render
    background.draw(screen, camera_offset, player)
    npc.draw_sprytek(screen, camera_offset)
    enemy_manager.draw(screen, camera_offset)
    background.draw_leaves(screen, camera_offset)
    inventory.update_inventory(keys, screen)
    npc.draw_chat_graphics(screen, player, camera_offset)

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
