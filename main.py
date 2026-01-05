import pygame
import time
import sys
from src.world import map_initialization, Background, calculate_camera_offset, Cabin
from src.entities import Player, Npc, EnemyManager
from src.ui import (
    Inventory, LoreDisplay, CATS_LORE, COLLECTIBLES_LORE, GameOverScreen,
    LoadingScreen, MainMenu, PauseMenu, OptionsMenu, CreditsScreen, GAME_TITLE,
    TutorialSystem, Minimap
)
from src.utils import preload_all_assets, clear_all_caches, resource_path
from src.save_system import save_game, load_game, load_settings, save_settings, delete_save, get_save_dir


# Game States
class GameState:
    LOADING = "loading"
    MAIN_MENU = "main_menu"
    PLAYING = "playing"
    PAUSED = "paused"
    OPTIONS = "options"
    CREDITS = "credits"
    GAME_OVER = "game_over"


# Initialize Pygame
pygame.init()
TILE_SIZE = 64

# Load settings and set display mode
settings = load_settings()
if settings.get('fullscreen', True):
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode((800, 600))

SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
clock = pygame.time.Clock()
pygame.display.set_caption(GAME_TITLE)

# Set window icon
try:
    icon = pygame.image.load(resource_path('graphics/character/character_idle.png'))
    pygame.display.set_icon(icon)
except Exception:
    pass  # Icon not critical

# Map constants
MAP_WIDTH, MAP_HEIGHT = 600, 600

# Game state
current_state = GameState.LOADING
previous_state = None  # For returning from options

# Current save slot
current_slot = None
map_seed = None
play_time = 0
play_time_start = 0

# UI screens (persistent)
loading_screen = LoadingScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
main_menu = MainMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
pause_menu = PauseMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
options_menu = OptionsMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
credits_screen = CreditsScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
game_over_screen = GameOverScreen(SCREEN_WIDTH, SCREEN_HEIGHT)

# Game objects (initialized when playing)
background = None
player = None
inventory = None
lore_display = None
cabin = None
npc = None
enemy_manager = None
spawn_point = None
tutorial = None
minimap = None

# Collection state
collect_cooldown = 0
f_key_pressed = False
g_key_pressed = False
c_key_pressed = False
v_key_pressed = False
is_brewing = False
brew_timer = 0

# ESC key state for debouncing
esc_pressed = False


def toggle_fullscreen(fullscreen):
    """Toggle fullscreen mode."""
    global screen, SCREEN_WIDTH, SCREEN_HEIGHT

    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((800, 600))
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

    # Clear image cache - surfaces need to be reconverted for new display
    from src.utils.asset_cache import _image_cache
    _image_cache.clear()

    # Recreate UI elements with new dimensions
    global loading_screen, main_menu, pause_menu, options_menu, credits_screen, game_over_screen

    # Save menu states before recreating
    options_was_showing = options_menu.is_showing
    options_settings = options_menu.settings.copy()
    options_selected = options_menu.selected_index
    pause_was_showing = pause_menu.is_showing
    pause_selected = pause_menu.selected_index

    loading_screen = LoadingScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
    main_menu = MainMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
    pause_menu = PauseMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
    options_menu = OptionsMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
    credits_screen = CreditsScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
    game_over_screen = GameOverScreen(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Restore options menu state
    if options_was_showing:
        options_menu.is_showing = True
        options_menu.settings = options_settings
        options_menu.selected_index = options_selected
        options_menu.input_cooldown = 30  # Prevent immediate input

    # Restore pause menu state
    if pause_was_showing:
        pause_menu.is_showing = True
        pause_menu.selected_index = pause_selected
        pause_menu.input_cooldown = 30

    # Update game objects if they exist (when toggling during gameplay)
    global background, inventory, lore_display, npc, minimap
    if background is not None:
        background.screen_width = SCREEN_WIDTH
        background.screen_height = SCREEN_HEIGHT
    if inventory is not None:
        inventory.screen_width = SCREEN_WIDTH
        inventory.screen_height = SCREEN_HEIGHT
    if lore_display is not None:
        lore_display.screen_width = SCREEN_WIDTH
        lore_display.screen_height = SCREEN_HEIGHT
    if npc is not None:
        npc.screen_width = SCREEN_WIDTH
        npc.screen_height = SCREEN_HEIGHT
    if minimap is not None:
        minimap.update_position(SCREEN_WIDTH, SCREEN_HEIGHT)


def init_new_game(slot, seed=None):
    """Initialize a new game in the given slot."""
    global background, player, inventory, lore_display, cabin, npc, enemy_manager, spawn_point, tutorial, minimap
    global current_slot, map_seed, play_time, play_time_start
    global collect_cooldown, f_key_pressed, g_key_pressed, c_key_pressed, v_key_pressed, is_brewing, brew_timer

    # Delete existing save if any
    delete_save(slot)

    # Clear caches to force new map generation
    clear_all_caches()

    # Initialize map with new seed
    grid, cat_positions, spawn_pt, used_seed = map_initialization(
        MAP_WIDTH, MAP_HEIGHT, num_cats=5, seed=seed
    )

    # Fallback values if map data is missing
    if spawn_pt is None:
        spawn_pt = (MAP_WIDTH // 2, MAP_HEIGHT // 2)
    if not cat_positions:
        cat_positions = []

    spawn_point = spawn_pt
    map_seed = used_seed
    current_slot = slot
    play_time = 0
    play_time_start = time.time()

    # Create game objects
    background = Background(MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, cat_positions, spawn_point=spawn_point, grid=grid)
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

    # Reset collection state
    collect_cooldown = 0
    f_key_pressed = False
    g_key_pressed = False
    c_key_pressed = False
    v_key_pressed = False
    is_brewing = False
    brew_timer = 0

    # Start tutorial if not completed yet
    current_settings = load_settings()
    if not current_settings.get('tutorial_completed', False):
        tutorial = TutorialSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
        tutorial.start()
    else:
        tutorial = None

    # Create minimap
    minimap = Minimap(SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE)


def load_saved_game(slot):
    """Load a game from the given slot."""
    global background, player, inventory, lore_display, cabin, npc, enemy_manager, spawn_point, tutorial, minimap
    global current_slot, map_seed, play_time, play_time_start
    global collect_cooldown, f_key_pressed, g_key_pressed, c_key_pressed, v_key_pressed, is_brewing, brew_timer

    save_data = load_game(slot)
    if save_data is None:
        return False

    # Clear caches
    clear_all_caches()

    # Load map with saved seed
    saved_seed = save_data.get('map_seed')
    grid, cat_positions, spawn_pt, used_seed = map_initialization(
        MAP_WIDTH, MAP_HEIGHT, num_cats=5, seed=saved_seed
    )

    if spawn_pt is None:
        spawn_pt = (MAP_WIDTH // 2, MAP_HEIGHT // 2)

    spawn_point = spawn_pt
    map_seed = saved_seed
    current_slot = slot
    play_time = save_data.get('play_time', 0)
    play_time_start = time.time()

    # Create background with saved cat positions
    cats_data = save_data.get('cats', {})
    remaining_cats = cats_data.get('remaining_positions', [])
    # Convert to tuple format if needed
    remaining_cats = [tuple(pos) if isinstance(pos, list) else pos for pos in remaining_cats]

    # Create game objects
    background = Background(MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT,
                           remaining_cats if remaining_cats else cat_positions, spawn_point=spawn_point, grid=grid)

    # Restore player state
    player_data = save_data.get('player', {})
    player_pos = player_data.get('position', [spawn_pt[0] * TILE_SIZE, spawn_pt[1] * TILE_SIZE])
    player = Player(SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, spawn_position=spawn_point)
    player.player_rect.x = player_pos[0]
    player.player_rect.y = player_pos[1]
    player.fatigue = player_data.get('fatigue', 100)

    inventory = Inventory(SCREEN_WIDTH, SCREEN_HEIGHT)
    lore_display = LoreDisplay(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Restore inventory state
    if player_data.get('has_coffee', False):
        inventory.fill_thermos()
    if player_data.get('carried_cat') is not None:
        inventory.pick_up_cat(player_data['carried_cat'])

    # Restore collectibles
    collectibles_data = save_data.get('collectibles', {})
    for coll_idx in collectibles_data.get('collected', []):
        inventory.add_collectible(coll_idx)

    # Create cabin and restore stored cats
    cabin = Cabin(spawn_point[0], spawn_point[1], TILE_SIZE)
    cabin_bounds = cabin.get_bounds()
    background.clear_trees_in_area(*cabin_bounds)

    for cat_idx in cats_data.get('stored', []):
        cabin.store_cat(cat_idx)

    # NPC
    sprytek_pos = cabin.get_sprytek_position()
    npc = Npc(SCREEN_WIDTH, SCREEN_HEIGHT, x=sprytek_pos[0], y=sprytek_pos[1])

    # Enemies
    enemy_manager = EnemyManager(TILE_SIZE, background.map_data, spawn_point, background.tree_positions, num_enemies=50)

    # Reset collection state
    collect_cooldown = 0
    f_key_pressed = False
    g_key_pressed = False
    c_key_pressed = False
    v_key_pressed = False
    is_brewing = False
    brew_timer = 0

    # No tutorial for loaded games
    tutorial = None

    # Create minimap and load visited tiles
    minimap = Minimap(SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE)
    visited_tiles = save_data.get('visited_tiles', [])
    if visited_tiles:
        minimap.set_visited_tiles(visited_tiles)

    return True


def save_current_game():
    """Save the current game state."""
    if current_slot is None or player is None:
        return False

    # Calculate total play time
    current_play_time = play_time + (time.time() - play_time_start)

    # Gather cat positions still on map
    remaining_cat_positions = [(x, y) for x, y, _ in background.cat_positions]

    # Gather game state
    game_state = {
        'play_time': current_play_time,
        'map_seed': map_seed,
        'map_size': [MAP_WIDTH, MAP_HEIGHT],
        'player': {
            'position': [player.player_rect.x, player.player_rect.y],
            'fatigue': player.fatigue,
            'has_coffee': inventory.has_coffee_available(),
            'carried_cat': inventory.carried_cat,
        },
        'cats': {
            'collected': [],  # Cats picked up but not stored
            'stored': list(cabin.stored_cats),
            'remaining_positions': remaining_cat_positions,
        },
        'collectibles': {
            'collected': list(inventory.collected_items),
            'remaining_positions': [(x, y) for x, y, _ in background.collectible_positions],
        },
        'visited_tiles': minimap.get_visited_tiles() if minimap else [],
    }

    return save_game(current_slot, game_state)


def restart_current_game():
    """Restart the current game (same slot, same map)."""
    if current_slot is None:
        return
    init_new_game(current_slot, seed=map_seed)


# Preload assets during loading screen
loading_complete = False


def do_loading():
    """Perform loading tasks."""
    global loading_complete
    loading_screen.set_progress(10, "Loading assets")
    preload_all_assets()
    loading_screen.set_progress(100, "Ready")
    loading_complete = True


# Main game loop
running = True
loading_started = False

while running:
    events = pygame.event.get()

    # Event handling
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # === LOADING STATE ===
    if current_state == GameState.LOADING:
        loading_screen.update()
        loading_screen.draw(screen)

        if not loading_started:
            loading_started = True
            do_loading()

        if loading_complete:
            current_state = GameState.MAIN_MENU
            main_menu.refresh_saves()

    # === MAIN MENU STATE ===
    elif current_state == GameState.MAIN_MENU:
        action, data = main_menu.update(keys, events)

        if action == "new_game":
            loading_screen.set_progress(50, "Generating world")
            loading_screen.draw(screen)
            pygame.display.flip()
            try:
                init_new_game(data)
                current_state = GameState.PLAYING
            except Exception as e:
                import traceback
                traceback.print_exc()
                main_menu.refresh_saves()

        elif action == "load_game":
            loading_screen.set_progress(50, "Loading save")
            loading_screen.draw(screen)
            pygame.display.flip()
            try:
                if load_saved_game(data):
                    current_state = GameState.PLAYING
                else:
                    # Load failed, stay in menu
                    main_menu.refresh_saves()
            except Exception as e:
                print(f"Error loading game: {e}")
                import traceback
                traceback.print_exc()
                main_menu.refresh_saves()

        elif action == "options":
            previous_state = GameState.MAIN_MENU
            options_menu.show()
            current_state = GameState.OPTIONS

        elif action == "credits":
            credits_screen.show()
            current_state = GameState.CREDITS

        elif action == "quit":
            running = False

        main_menu.draw(screen)

    # === PLAYING STATE ===
    elif current_state == GameState.PLAYING:
        # Handle ESC for pause menu
        if keys[pygame.K_ESCAPE] and not esc_pressed:
            pause_menu.show()
            current_state = GameState.PAUSED
            esc_pressed = True
        elif not keys[pygame.K_ESCAPE]:
            esc_pressed = False

        # Handle game over screen
        if game_over_screen.is_showing:
            result = game_over_screen.update(keys)
            if result == "restart":
                restart_current_game()

            # Render game in background (frozen)
            camera_offset = calculate_camera_offset(player, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT)
            background.draw(screen, camera_offset, player, cabin, enemy_manager)
            npc.draw_sprytek(screen, camera_offset)
            background.draw_leaf_particles(screen, camera_offset)
            game_over_screen.draw(screen)
            pygame.display.flip()
            clock.tick(60)
            continue

        # If lore display is showing, only update that and block other input
        if lore_display.is_showing:
            lore_display.update(keys)

            camera_offset = calculate_camera_offset(player, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT)
            background.draw(screen, camera_offset, player, cabin, enemy_manager)
            npc.draw_sprytek(screen, camera_offset)
            background.draw_leaf_particles(screen, camera_offset)
            stored_cats = cabin.get_stored_cat_count()
            inventory.update_inventory(keys, screen, stored_cats, player.get_fatigue_percent())
            npc.draw_chat_graphics(screen, player, camera_offset)
            lore_display.draw(screen)

            pygame.display.flip()
            clock.tick(60)
            continue

        # Update game objects (don't move player when inventory is open)
        if not inventory.inventory_open:
            player.update(keys, clock, npc, background, cabin)
        npc.update(keys, player)
        enemy_manager.update(clock.get_time(), player.player_rect)

        # Update fatigue
        player.update_fatigue(clock.get_time())

        # Check if player fell asleep
        if player.is_exhausted():
            game_over_screen.show("You fell asleep!")
            continue

        # Check enemy collision
        if enemy_manager.check_player_collision(player.player_rect):
            game_over_screen.show("Voice caught you!")
            continue

        # Collection cooldown
        if collect_cooldown > 0:
            collect_cooldown -= 1

        # Check cat proximity and handle picking up
        cat_index, cat_image_index = background.check_cat_proximity(player.player_rect)
        if cat_index is not None and not inventory.is_carrying_cat():
            inventory.set_collect_hint(True)
            inventory.set_collectible_hint(False)
            if keys[pygame.K_f] and not f_key_pressed and not npc.is_talking and collect_cooldown == 0:
                collected = background.collect_cat(cat_index)
                if collected:
                    inventory.pick_up_cat(cat_image_index)
                    lore_display.show_lore(CATS_LORE[cat_image_index], background.cat_images[cat_image_index])
                    collect_cooldown = 30
        else:
            inventory.set_collect_hint(False)

            coll_index, coll_item_index = background.check_collectible_proximity(player.player_rect)
            if coll_index is not None:
                inventory.set_collectible_hint(True)
                if keys[pygame.K_f] and not f_key_pressed and not npc.is_talking and collect_cooldown == 0:
                    collected = background.collect_collectible(coll_index)
                    if collected:
                        inventory.add_collectible(coll_item_index)
                        lore_display.show_lore(COLLECTIBLES_LORE[coll_item_index], background.collectible_images[coll_item_index])
                        collect_cooldown = 30
            else:
                inventory.set_collectible_hint(False)

        f_key_pressed = keys[pygame.K_f]

        # Check if player is inside cabin
        player_inside_cabin = cabin.is_player_inside(player.player_rect)
        if player_inside_cabin:
            inventory.set_storage_hint(True)
            if keys[pygame.K_g] and not g_key_pressed and collect_cooldown == 0:
                if inventory.is_carrying_cat():
                    cat_idx = inventory.put_down_cat()
                    if cat_idx is not None:
                        cabin.store_cat(cat_idx)
                    collect_cooldown = 30
        else:
            inventory.set_storage_hint(False)

        g_key_pressed = keys[pygame.K_g]

        # Coffee machine interaction
        if player_inside_cabin and cabin.is_near_coffee_machine(player.player_rect):
            if not is_brewing:
                if not inventory.has_coffee_available():
                    inventory.set_coffee_hint(True, "brew")
                    if keys[pygame.K_c] and not c_key_pressed and collect_cooldown == 0:
                        is_brewing = True
                        brew_timer = 3000
                        collect_cooldown = 30
                else:
                    inventory.set_coffee_hint(False)
            else:
                inventory.set_coffee_hint(False)
        else:
            inventory.set_coffee_hint(False)

        # Brewing process
        if is_brewing:
            brew_timer -= clock.get_time()
            if brew_timer <= 0:
                is_brewing = False
                inventory.fill_thermos()

        # Drink coffee
        if inventory.has_coffee_available() and not is_brewing:
            if not (player_inside_cabin and cabin.is_near_coffee_machine(player.player_rect)):
                inventory.set_coffee_hint(True, "drink")
            if keys[pygame.K_v] and not v_key_pressed and collect_cooldown == 0:
                if inventory.drink_coffee():
                    player.drink_coffee()
                    collect_cooldown = 30

        c_key_pressed = keys[pygame.K_c]
        v_key_pressed = keys[pygame.K_v]

        # Render
        camera_offset = calculate_camera_offset(player, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT)
        brew_progress = 0
        if is_brewing:
            brew_progress = 1.0 - (brew_timer / 3000)

        # Update leaf particles (world-based)
        dt = clock.get_time() / 1000.0  # Convert ms to seconds
        background.update_leaf_particles(dt, camera_offset, cabin)

        background.draw(screen, camera_offset, player, cabin, enemy_manager, is_brewing, brew_progress)
        npc.draw_sprytek(screen, camera_offset)

        # Draw leaf particles (world-based overlay)
        background.draw_leaf_particles(screen, camera_offset)

        stored_cats = cabin.get_stored_cat_count()
        inventory.update_inventory(keys, screen, stored_cats, player.get_fatigue_percent())
        npc.draw_chat_graphics(screen, player, camera_offset)

        # Draw cabin arrow indicator when cabin is off-screen
        background.draw_cabin_arrow(screen, player.player_rect, cabin, camera_offset)

        # Update and draw minimap
        if minimap:
            player_tile_x = player.player_rect.centerx // TILE_SIZE
            player_tile_y = player.player_rect.centery // TILE_SIZE
            minimap.update(player_tile_x, player_tile_y)
            minimap.draw(screen, background.map_data, player_tile_x, player_tile_y, cabin, background.cat_positions)

        # Update and draw tutorial if active
        if tutorial is not None and tutorial.is_active:
            tutorial.update(keys, npc, inventory)
            tutorial.draw(screen)

            # Save settings when tutorial is completed
            if tutorial.is_completed():
                current_settings = load_settings()
                current_settings['tutorial_completed'] = True
                save_settings(current_settings)

    # === PAUSED STATE ===
    elif current_state == GameState.PAUSED:
        action, data = pause_menu.update(keys, events)

        if action == "resume":
            current_state = GameState.PLAYING

        elif action == "save":
            success = save_current_game()
            pause_menu.show_save_message(success)

        elif action == "options":
            previous_state = GameState.PAUSED
            options_menu.show()
            current_state = GameState.OPTIONS

        elif action == "main_menu":
            save_current_game()  # Auto-save before leaving
            current_state = GameState.MAIN_MENU
            main_menu.state = MainMenu.STATE_MAIN
            main_menu.refresh_saves()

        elif action == "quit":
            save_current_game()  # Auto-save before quitting
            running = False

        # Draw game in background
        camera_offset = calculate_camera_offset(player, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT)
        background.draw(screen, camera_offset, player, cabin, enemy_manager)
        npc.draw_sprytek(screen, camera_offset)
        background.draw_leaf_particles(screen, camera_offset)
        stored_cats = cabin.get_stored_cat_count()
        # Close inventory and block toggle during pause
        inventory.inventory_open = False
        inventory.toggle_pressed = True  # Block E key from opening inventory
        inventory.update_inventory(keys, screen, stored_cats, player.get_fatigue_percent())
        npc.draw_chat_graphics(screen, player, camera_offset)

        # Draw pause menu on top
        pause_menu.draw(screen)

    # === OPTIONS STATE ===
    elif current_state == GameState.OPTIONS:
        action, data = options_menu.update(keys, events)

        if action == "toggle_fullscreen":
            toggle_fullscreen(data)

        elif action == "back":
            current_state = previous_state if previous_state else GameState.MAIN_MENU
            # Set cooldown to prevent ESC from immediately quitting main menu
            if current_state == GameState.MAIN_MENU:
                main_menu.reset_cooldown()

        # Draw background based on previous state
        if previous_state == GameState.PAUSED and player is not None:
            camera_offset = calculate_camera_offset(player, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT)
            background.draw(screen, camera_offset, player, cabin, enemy_manager)
            npc.draw_sprytek(screen, camera_offset)
            background.draw_leaf_particles(screen, camera_offset)
        else:
            screen.fill((25, 25, 35))

        options_menu.draw(screen)

    # === CREDITS STATE ===
    elif current_state == GameState.CREDITS:
        action = credits_screen.update(keys, events)

        if action == "back":
            current_state = GameState.MAIN_MENU
            main_menu.reset_cooldown()

        credits_screen.draw(screen)

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
