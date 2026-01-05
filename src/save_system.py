"""Save/Load system for Mind of Seasons."""

import json
import os
from pathlib import Path
from datetime import datetime


def get_save_dir() -> Path:
    """Get the save directory path, creating it if necessary."""
    if os.name == 'nt':  # Windows
        appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
        save_dir = Path(appdata) / 'MindOfSeasons' / 'saves'
    else:  # Linux/Mac
        save_dir = Path.home() / '.mindofseasons' / 'saves'

    save_dir.mkdir(parents=True, exist_ok=True)
    return save_dir


def get_settings_path() -> Path:
    """Get the settings file path."""
    save_dir = get_save_dir().parent
    return save_dir / 'settings.json'


def _get_save_path(slot: int) -> Path:
    """Get the path for a specific save slot."""
    return get_save_dir() / f'save_{slot}.json'


def save_game(slot: int, game_state: dict) -> bool:
    """
    Save game state to a slot.

    Args:
        slot: Save slot number (1-3)
        game_state: Dictionary containing all game state

    Returns:
        True if save was successful, False otherwise
    """
    try:
        save_path = _get_save_path(slot)

        # Add metadata
        save_data = {
            'version': '1.0.0',
            'slot': slot,
            'created': game_state.get('created', datetime.now().isoformat()),
            'last_saved': datetime.now().isoformat(),
            'play_time': game_state.get('play_time', 0),
            'map_seed': game_state.get('map_seed'),
            'map_size': game_state.get('map_size', [600, 600]),
            'player': game_state.get('player', {}),
            'cats': game_state.get('cats', {}),
            'collectibles': game_state.get('collectibles', {}),
            'visited_tiles': game_state.get('visited_tiles', []),
        }

        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2)

        return True
    except Exception as e:
        print(f"Error saving game: {e}")
        return False


def load_game(slot: int) -> dict | None:
    """
    Load game state from a slot.

    Args:
        slot: Save slot number (1-3)

    Returns:
        Dictionary containing game state, or None if load failed
    """
    try:
        save_path = _get_save_path(slot)

        if not save_path.exists():
            return None

        with open(save_path, 'r', encoding='utf-8') as f:
            save_data = json.load(f)

        return save_data
    except Exception as e:
        print(f"Error loading game: {e}")
        return None


def delete_save(slot: int) -> bool:
    """
    Delete a save slot.

    Args:
        slot: Save slot number (1-3)

    Returns:
        True if deletion was successful, False otherwise
    """
    try:
        save_path = _get_save_path(slot)

        if save_path.exists():
            save_path.unlink()

        return True
    except Exception as e:
        print(f"Error deleting save: {e}")
        return False


def get_save_info(slot: int) -> dict | None:
    """
    Get preview info for a save slot (without loading full state).

    Args:
        slot: Save slot number (1-3)

    Returns:
        Dictionary with slot preview info, or None if slot is empty
    """
    save_data = load_game(slot)

    if save_data is None:
        return None

    # Extract preview info
    cats_data = save_data.get('cats', {})
    stored_cats = len(cats_data.get('stored', []))
    total_cats = 5  # Fixed number of cats

    collectibles_data = save_data.get('collectibles', {})
    collected_collectibles = len(collectibles_data.get('collected', []))
    total_collectibles = 10  # Fixed number of collectibles

    # Map exploration percentage
    visited_tiles = save_data.get('visited_tiles', [])
    map_size = save_data.get('map_size', [600, 600])
    total_tiles = map_size[0] * map_size[1]
    exploration_percent = int((len(visited_tiles) / total_tiles) * 100) if total_tiles > 0 else 0

    # Format play time
    play_time_seconds = save_data.get('play_time', 0)
    minutes = int(play_time_seconds // 60)
    seconds = int(play_time_seconds % 60)

    return {
        'slot': slot,
        'stored_cats': stored_cats,
        'total_cats': total_cats,
        'collected_collectibles': collected_collectibles,
        'total_collectibles': total_collectibles,
        'exploration_percent': exploration_percent,
        'play_time': play_time_seconds,
        'play_time_formatted': f"{minutes}:{seconds:02d}",
        'is_complete': stored_cats >= total_cats,
        'last_saved': save_data.get('last_saved', save_data.get('created', '')),
    }


def list_saves() -> list[dict | None]:
    """
    Get info for all save slots.

    Returns:
        List of 3 items, each being save info dict or None for empty slots
    """
    return [get_save_info(slot) for slot in range(1, 4)]


def save_settings(settings: dict) -> bool:
    """
    Save game settings.

    Args:
        settings: Dictionary containing settings

    Returns:
        True if save was successful, False otherwise
    """
    try:
        settings_path = get_settings_path()
        settings_path.parent.mkdir(parents=True, exist_ok=True)

        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)

        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False


def load_settings() -> dict:
    """
    Load game settings.

    Returns:
        Dictionary containing settings, or defaults if not found
    """
    defaults = {
        'fullscreen': False,
        'master_volume': 80,
        'music_volume': 60,
        'sfx_volume': 100,
        'tutorial_completed': False,
    }

    try:
        settings_path = get_settings_path()

        if not settings_path.exists():
            return defaults

        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        # Merge with defaults to ensure all keys exist
        return {**defaults, **settings}
    except Exception as e:
        print(f"Error loading settings: {e}")
        return defaults
