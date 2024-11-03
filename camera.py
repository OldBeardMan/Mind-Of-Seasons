#TODO zrobić aby kamera się tak poklatkowo nie przesuwała i żeby sprytek za nami nie podążał

def calculate_camera_offset(player, map_width, map_height, tile_size, screen_width, screen_height):
    # Dokładna pozycja gracza w pixelach
    exact_x = player.player_rect.x
    exact_y = player.player_rect.y

    # Przesunięcie kamery z uwzględnieniem środka ekranu
    offset_x = exact_x - screen_width // 2
    offset_y = exact_y - screen_height // 2

    # Przesunięcie kamery, aby nie wychodziło poza granice mapy
    offset_x = max(0, min(offset_x, map_width * tile_size - screen_width))
    offset_y = max(0, min(offset_y, map_height * tile_size - screen_height))

    return offset_x, offset_y
