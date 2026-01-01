"""
Global asset cache to prevent reloading resources on respawn.
Assets are loaded once and cached for the entire game session.
"""
import pygame
from src.utils.resource_path import resource_path

# Global cache storage
_image_cache = {}
_font_cache = {}
_map_cache = {}
_tree_cache = {}  # Cache for generated tree positions
_enemy_spawn_cache = {}  # Cache for enemy spawn positions
_initialized = False


def _ensure_initialized():
    """Ensure pygame is initialized for asset loading."""
    global _initialized
    if not _initialized:
        pygame.font.init()
        _initialized = True


def get_image(path, size=None, convert_alpha=True):
    """
    Load and cache an image. Returns cached version if already loaded.

    Args:
        path: Relative path to image file
        size: Optional (width, height) tuple to scale the image
        convert_alpha: Whether to convert with alpha channel

    Returns:
        pygame.Surface
    """
    # Create cache key including size
    cache_key = (path, size)

    if cache_key in _image_cache:
        return _image_cache[cache_key]

    # Load image
    try:
        img = pygame.image.load(resource_path(path))
        if convert_alpha:
            img = img.convert_alpha()
        else:
            img = img.convert()

        if size:
            img = pygame.transform.scale(img, size)

        _image_cache[cache_key] = img
        return img
    except Exception as e:
        print(f"Warning: Could not load image {path}: {e}")
        return None


def get_font(size):
    """
    Load and cache the game font at specified size.

    Args:
        size: Font size in pixels

    Returns:
        pygame.font.Font
    """
    _ensure_initialized()

    if size in _font_cache:
        return _font_cache[size]

    font = pygame.font.Font(resource_path('fonts/PressStart2P.ttf'), size)
    _font_cache[size] = font
    return font


def preload_all_assets():
    """
    Preload all game assets at startup for faster loading.
    Call this once at game initialization.
    """
    from src.ui.lore_data import CATS_LORE, COLLECTIBLES_LORE

    # Constants (must match those in background.py)
    TILE_SIZE = 64
    TREE_SIZE = 128
    COLLECTIBLE_SIZE = 48

    # Background tiles
    get_image('graphics/landscape/tile.png', (TILE_SIZE, TILE_SIZE))
    get_image('graphics/landscape/path.png', (TILE_SIZE, TILE_SIZE))

    # Leaves animation (5 frames)
    for i in range(5):
        get_image(f'graphics/landscape/leaves/{i}.png', (128, 128))

    # Trees (2 variants)
    for i in range(1, 3):
        get_image(f'graphics/landscape/tree{i}.png', (TREE_SIZE, TREE_SIZE))

    # Cat images (for background - 64x64 and inventory - 50x50)
    for cat in CATS_LORE:
        if "image" in cat:
            path = f'graphics/npc/{cat["image"]}'
            get_image(path, (TREE_SIZE // 2, TREE_SIZE // 2))  # 64x64 for background
            get_image(path, (50, 50))  # 50x50 for inventory

    # Collectible images (for background - 48x48 and inventory - 40x40)
    for item in COLLECTIBLES_LORE:
        if "image" in item:
            path = f'graphics/landscape/{item["image"]}'
            get_image(path, (COLLECTIBLE_SIZE, COLLECTIBLE_SIZE))  # 48x48 for background
            get_image(path, (40, 40))  # 40x40 for inventory

    # Enemy sprites (4 frames, indexed 1-4)
    for i in range(1, 5):
        get_image(f'graphics/npc/enemy/enemy{i}.png', (80, 80))

    # Player sprites (70x70)
    get_image('graphics/character/character_idle.png', (70, 70))
    get_image('graphics/character/character_walk1.png', (70, 70))
    get_image('graphics/character/character_walk2.png', (70, 70))

    # NPC Sprytek (60x70)
    get_image('graphics/npc/sprytek.png', (60, 70))

    # Preload all font sizes used in the game (including menu fonts)
    for size in [7, 8, 9, 10, 12, 14, 16, 20, 24, 28, 32, 36]:
        get_font(size)


def get_cached_trees(cache_key):
    """Get cached tree positions if available."""
    return _tree_cache.get(cache_key)


def set_cached_trees(cache_key, trees, tree_chunks, collision_chunks):
    """Cache tree positions and chunks."""
    _tree_cache[cache_key] = {
        'trees': trees[:],  # Copy list
        'tree_chunks': {k: v[:] for k, v in tree_chunks.items()},
        'collision_chunks': {k: v[:] for k, v in collision_chunks.items()}
    }


def get_cached_enemy_spawns(cache_key):
    """Get cached enemy spawn positions if available."""
    return _enemy_spawn_cache.get(cache_key)


def set_cached_enemy_spawns(cache_key, positions):
    """Cache enemy spawn positions."""
    _enemy_spawn_cache[cache_key] = positions[:]


def clear_cache():
    """Clear all cached assets. Useful for memory management."""
    global _image_cache, _font_cache, _map_cache, _tree_cache, _enemy_spawn_cache
    _image_cache.clear()
    _font_cache.clear()
    _map_cache.clear()
    _tree_cache.clear()
    _enemy_spawn_cache.clear()


def clear_all_caches():
    """Clear map and game-related caches (keeps images/fonts for performance)."""
    global _map_cache, _tree_cache, _enemy_spawn_cache
    _map_cache.clear()
    _tree_cache.clear()
    _enemy_spawn_cache.clear()
