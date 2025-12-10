def calculate_camera_offset(player, map_width, map_height, tile_size, screen_width, screen_height):
    """
    Calculate camera offset to center on player while staying within map bounds.

    Returns: (offset_x, offset_y) tuple
    """
    # Center camera on player
    offset_x = player.player_rect.x - screen_width // 2
    offset_y = player.player_rect.y - screen_height // 2

    # Clamp to map boundaries
    max_x = map_width * tile_size - screen_width
    max_y = map_height * tile_size - screen_height

    offset_x = max(0, min(offset_x, max_x))
    offset_y = max(0, min(offset_y, max_y))

    return offset_x, offset_y
