import pygame

def load_inventory_graphics(screen_width, screen_height):
    image_inventory = pygame.image.load('Grafiki/UI/Slot.png').convert_alpha()
    image_inventory = pygame.transform.scale(image_inventory, (screen_width // 1.9, screen_height // 1.2))
    return image_inventory

def load_cat_images():
    """Ładuje obrazki kotków do wyświetlania w inventory"""
    cat_images = []
    for i in [2, 3, 5]:
        cat_img = pygame.image.load(f'Grafiki/NPC/Cat{i}.png').convert_alpha()
        cat_img = pygame.transform.scale(cat_img, (50, 50))  # Mniejszy rozmiar do inventory
        cat_images.append(cat_img)
    return cat_images

class Inventory:
    def __init__(self, screen_width, screen_height):
        # Ładowanie grafiki ekwipunku
        self.inventory_image = load_inventory_graphics(screen_width, screen_height)
        self.inventory_rect = self.inventory_image.get_rect(center=(screen_width // 2, screen_height // 2))
        self.inventory_open = False
        self.toggle_pressed = False
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Lista zebranych kotków (przechowuje indeksy obrazków)
        self.collected_cats = []
        self.cat_images = load_cat_images()

        # Font do wyświetlania licznika (pixelowy)
        pygame.font.init()
        self.font = pygame.font.Font('Czcionki/PressStart2P.ttf', 12)
        self.small_font = pygame.font.Font('Czcionki/PressStart2P.ttf', 8)

        # Podpowiedź zbierania
        self.show_collect_hint = False
        self.hint_font = pygame.font.Font('Czcionki/PressStart2P.ttf', 10)

    def add_cat(self, cat_image_index):
        """Dodaje kotka do inventory"""
        self.collected_cats.append(cat_image_index)

    def get_cat_count(self):
        """Zwraca liczbę zebranych kotków"""
        return len(self.collected_cats)

    def update_inventory(self, keys, screen):
        # Zmienna do śledzenia, czy ekwipunek jest otwarty
        if keys[pygame.K_e] and not self.toggle_pressed:
            self.inventory_open = not self.inventory_open
            self.toggle_pressed = True

        if not keys[pygame.K_e]:
            self.toggle_pressed = False

        # Rysowanie ekwipunku, jeśli jest otwarty
        if self.inventory_open:
            screen.blit(self.inventory_image, self.inventory_rect)
            self._draw_collected_cats(screen)

        # Zawsze rysuj licznik kotków w rogu ekranu
        self._draw_cat_counter(screen)

        # Rysuj podpowiedź zbierania jeśli gracz jest blisko kotka
        if self.show_collect_hint:
            self._draw_collect_hint(screen)

    def _draw_collected_cats(self, screen):
        """Draw collected cats in inventory"""
        if not self.collected_cats:
            # Show message when inventory is empty
            empty_text = self.font.render("No cats yet", True, (100, 100, 100))
            text_rect = empty_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            screen.blit(empty_text, text_rect)
            return

        # Parametry slotów
        slot_size = 60
        slots_per_row = 6
        start_x = self.inventory_rect.x + 80
        start_y = self.inventory_rect.y + 100

        for i, cat_index in enumerate(self.collected_cats):
            row = i // slots_per_row
            col = i % slots_per_row

            slot_x = start_x + col * (slot_size + 15)
            slot_y = start_y + row * (slot_size + 15)

            # Rysuj ramkę slotu
            slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)
            pygame.draw.rect(screen, (80, 60, 40), slot_rect, 3, border_radius=5)

            # Rysuj kotka w slocie
            cat_img = self.cat_images[cat_index]
            cat_rect = cat_img.get_rect(center=slot_rect.center)
            screen.blit(cat_img, cat_rect)

    def _draw_cat_counter(self, screen):
        """Draw cat counter in corner of screen"""
        counter_text = f"Cats: {len(self.collected_cats)}"
        text_surface = self.font.render(counter_text, True, (255, 255, 255))

        # Tło licznika
        padding = 10
        bg_rect = pygame.Rect(
            10,
            10,
            text_surface.get_width() + padding * 2,
            text_surface.get_height() + padding * 2
        )
        pygame.draw.rect(screen, (50, 50, 50, 180), bg_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 80, 60), bg_rect, 2, border_radius=8)

        screen.blit(text_surface, (10 + padding, 10 + padding))

    def _draw_collect_hint(self, screen):
        """Draw hint for collecting cat"""
        hint_text = "[F] Collect cat"
        hint_surface = self.hint_font.render(hint_text, True, (255, 255, 200))

        # Pozycja na środku dolnej części ekranu
        hint_x = (self.screen_width - hint_surface.get_width()) // 2
        hint_y = self.screen_height - 100

        # Tło podpowiedzi
        padding = 8
        bg_rect = pygame.Rect(
            hint_x - padding,
            hint_y - padding,
            hint_surface.get_width() + padding * 2,
            hint_surface.get_height() + padding * 2
        )
        pygame.draw.rect(screen, (40, 40, 40, 200), bg_rect, border_radius=6)
        pygame.draw.rect(screen, (200, 180, 100), bg_rect, 2, border_radius=6)

        screen.blit(hint_surface, (hint_x, hint_y))

    def set_collect_hint(self, show):
        """Ustawia czy pokazywać podpowiedź zbierania"""
        self.show_collect_hint = show