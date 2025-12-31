import pygame
from src.world import map_initialization, Background, calculate_camera_offset, Cabin
from src.entities import Player, Npc, EnemyManager
from src.ui import Inventory, LoreDisplay, CATS_LORE, COLLECTIBLES_LORE
from src.utils import preload_all_assets

# Initialize Pygame
pygame.init()
TILE_SIZE = 64
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
clock = pygame.time.Clock()
pygame.display.set_caption("Mind of Seasons")

# Preload all assets at startup (prevents lag on respawn)
preload_all_assets()


def init_game():
    """Initialize or restart the game."""
    # Initialize map and get cat/spawn positions
    MAP_WIDTH, MAP_HEIGHT = 600, 600
    cat_positions, spawn_point = map_initialization(MAP_WIDTH, MAP_HEIGHT, num_cats=5)

    # Fallback values if map data is missing
    if spawn_point is None:
        spawn_point = (MAP_WIDTH // 2, MAP_HEIGHT // 2)
    if not cat_positions:
        cat_positions = []

    # Create game objects
    background = Background(MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, cat_positions, spawn_point=spawn_point)
    player = Player(SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, spawn_position=spawn_point)
    inventory = Inventory(SCREEN_WIDTH, SCREEN_HEIGHT)
    lore_display = LoreDisplay(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Create cabin at spawn point
    cabin = Cabin(spawn_point[0], spawn_point[1], TILE_SIZE)

    # Clear trees around cabin
    cabin_bounds = cabin.get_bounds()
    background.clear_trees_in_area(*cabin_bounds)

    # NPC (Sprytek) spawns in front of cabin
    sprytek_pos = cabin.get_sprytek_position()
    npc = Npc(SCREEN_WIDTH, SCREEN_HEIGHT, x=sprytek_pos[0], y=sprytek_pos[1])

    # Enemies spawn (not in trees)
    enemy_manager = EnemyManager(TILE_SIZE, background.map_data, spawn_point, background.tree_positions, num_enemies=50)

    return background, player, inventory, lore_display, cabin, npc, enemy_manager, spawn_point, MAP_WIDTH, MAP_HEIGHT


# Initialize game
background, player, inventory, lore_display, cabin, npc, enemy_manager, spawn_point, MAP_WIDTH, MAP_HEIGHT = init_game()

# Collection state
collect_cooldown = 0
f_key_pressed = False
g_key_pressed = False

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

    # If lore display is showing, only update that and block other input
    if lore_display.is_showing:
        lore_display.update(keys)

        # Still render background but don't update game logic
        camera_offset = calculate_camera_offset(player, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT)
        background.draw(screen, camera_offset, player, cabin, enemy_manager)
        npc.draw_sprytek(screen, camera_offset)
        background.draw_leaves(screen, camera_offset)
        stored_cats = cabin.get_stored_cat_count()
        inventory.update_inventory(keys, screen, stored_cats)
        npc.draw_chat_graphics(screen, player, camera_offset)

        # Draw lore display on top
        lore_display.draw(screen)

        pygame.display.flip()
        clock.tick(60)
        continue

    # Update game objects
    player.update(keys, clock, npc, background, cabin)
    npc.update(keys, player)
    enemy_manager.update(clock.get_time(), player.player_rect)

    # Check enemy collision - restart game if hit
    if enemy_manager.check_player_collision(player.player_rect):
        background, player, inventory, lore_display, cabin, npc, enemy_manager, spawn_point, MAP_WIDTH, MAP_HEIGHT = init_game()
        collect_cooldown = 0
        f_key_pressed = False
        g_key_pressed = False
        continue

    # Collection cooldown
    if collect_cooldown > 0:
        collect_cooldown -= 1

    # Check cat proximity and handle picking up (only if not carrying one)
    cat_index, cat_image_index = background.check_cat_proximity(player.player_rect)
    if cat_index is not None and not inventory.is_carrying_cat():
        inventory.set_collect_hint(True)
        inventory.set_collectible_hint(False)
        # Pick up cat with F key (not during NPC dialogue, with cooldown)
        if keys[pygame.K_f] and not f_key_pressed and not npc.is_talking and collect_cooldown == 0:
            collected = background.collect_cat(cat_index)
            if collected:
                inventory.pick_up_cat(cat_image_index)
                # Show lore for picked up cat
                lore_display.show_lore(CATS_LORE[cat_image_index], background.cat_images[cat_image_index])
                collect_cooldown = 30
    else:
        inventory.set_collect_hint(False)

        # Check collectible proximity (items go to inventory)
        coll_index, coll_item_index = background.check_collectible_proximity(player.player_rect)
        if coll_index is not None:
            inventory.set_collectible_hint(True)
            # Collect item with F key (not during NPC dialogue, with cooldown)
            if keys[pygame.K_f] and not f_key_pressed and not npc.is_talking and collect_cooldown == 0:
                collected = background.collect_collectible(coll_index)
                if collected:
                    inventory.add_collectible(coll_item_index)
                    # Show lore for collected item
                    lore_display.show_lore(COLLECTIBLES_LORE[coll_item_index], background.collectible_images[coll_item_index])
                    collect_cooldown = 30
        else:
            inventory.set_collectible_hint(False)

    f_key_pressed = keys[pygame.K_f]

    # Check if player is inside cabin and handle storing cat
    player_inside_cabin = cabin.is_player_inside(player.player_rect)
    if player_inside_cabin:
        inventory.set_storage_hint(True)
        # Store carried cat with G key
        if keys[pygame.K_g] and not g_key_pressed and collect_cooldown == 0:
            if inventory.is_carrying_cat():
                cat_idx = inventory.put_down_cat()
                if cat_idx is not None:
                    cabin.store_cat(cat_idx)
                collect_cooldown = 30
    else:
        inventory.set_storage_hint(False)

    g_key_pressed = keys[pygame.K_g]

    # Calculate camera offset
    camera_offset = calculate_camera_offset(player, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT)

    # Render
    background.draw(screen, camera_offset, player, cabin, enemy_manager)
    npc.draw_sprytek(screen, camera_offset)
    background.draw_leaves(screen, camera_offset)
    stored_cats = cabin.get_stored_cat_count()
    inventory.update_inventory(keys, screen, stored_cats)
    npc.draw_chat_graphics(screen, player, camera_offset)

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
