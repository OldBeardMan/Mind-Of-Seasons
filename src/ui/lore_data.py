# Lore data loader - loads cats and collectibles from JSON files
import json
from src.utils import resource_path


def _load_json(filename):
    """Load JSON data from file."""
    with open(resource_path(filename), 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Convert color arrays to tuples
    for item in data:
        if 'color' in item:
            item['color'] = tuple(item['color'])
    return data


# Load data from JSON files
CATS_LORE = _load_json('data/cats.json')
COLLECTIBLES_LORE = _load_json('data/collectibles.json')
