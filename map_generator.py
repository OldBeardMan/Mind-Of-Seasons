#TODO zrobić aby kamera się tak poklatkowo nie przesuwała i żeby sprytek za nami nie podążał

def calculate_camera_offset(player, map_width, map_height, tile_size, screen_width, screen_height):
    offset_x = player.map_position[0] * tile_size - screen_width // 2
    offset_y = player.map_position[1] * tile_size - screen_height // 2
    offset_x = max(0, min(offset_x, map_width * tile_size - screen_width))
    offset_y = max(0, min(offset_y, map_height * tile_size - screen_height))
    return offset_x, offset_y
