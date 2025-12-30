import pygame
from src.ui.lore_display import create_placeholder
from src.ui.lore_data import CATS_LORE, COLLECTIBLES_LORE

def load_inventory_graphics(screen_width, screen_height):
    image_inventory = pygame.image.load('Grafiki/UI/Slot.png').convert_alpha()
    image_inventory = pygame.transform.scale(image_inventory, (screen_width // 1.9, screen_height // 1.2))
    return image_inventory

def load_cat_images():
    """Ładuje obrazki kotków do wyświetlania"""
    cat_images = []
    for cat in CATS_LORE:
        if "image" in cat:
            try:
                cat_img = pygame.image.load(f'Grafiki/NPC/{cat["image"]}').convert_alpha()
                cat_img = pygame.transform.scale(cat_img, (50, 50))
            except:
                cat_img = create_placeholder((50, 50), cat["color"], cat["name"])
        else:
            cat_img = create_placeholder((50, 50), cat["color"], cat["name"])
        cat_images.append(cat_img)
    return cat_images

def load_collectible_images():
    """Ładuje obrazki znajdziek do wyświetlania w inventory"""
    coll_images = []
    for item in COLLECTIBLES_LORE:
        if "image" in item:
            try:
                coll_img = pygame.image.load(f'Grafiki/Landscape/{item["image"]}').convert_alpha()
                coll_img = pygame.transform.scale(coll_img, (40, 40))
            except:
                coll_img = create_placeholder((40, 40), item["color"], item["name"])
        else:
            coll_img = create_placeholder((40, 40), item["color"], item["name"])
        coll_images.append(coll_img)
    return coll_images

class Inventory:
    def __init__(self, screen_width, screen_height):
        # Ładowanie grafiki ekwipunku
        self.inventory_image = load_inventory_graphics(screen_width, screen_height)
        self.inventory_rect = self.inventory_image.get_rect(center=(screen_width // 2, screen_height // 2))
        self.inventory_open = False
        self.toggle_pressed = False
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Obrazki kotków (do wyświetlania noszonego kotka)
        self.cat_images = load_cat_images()

        # Lista zebranych znajdziek (tylko itemy, nie kotki!)
        self.collected_items = []
        self.collectible_images = load_collectible_images()

        # System noszenia kotka na rękach (tylko jeden naraz!)
        self.carried_cat = None  # Indeks noszonego kotka lub None

        # Font do wyświetlania licznika (pixelowy)
        pygame.font.init()
        self.font = pygame.font.Font('Czcionki/PressStart2P.ttf', 12)
        self.small_font = pygame.font.Font('Czcionki/PressStart2P.ttf', 8)

        # Podpowiedź zbierania
        self.show_collect_hint = False
        self.show_collectible_hint = False
        self.hint_font = pygame.font.Font('Czcionki/PressStart2P.ttf', 10)

        # System przechowywania w chatce
        self.show_storage_hint = False

    def pick_up_cat(self, cat_index):
        """Podnosi kotka na ręce. Zwraca True jeśli udało się podnieść."""
        if self.carried_cat is None:
            self.carried_cat = cat_index
            return True
        return False

    def is_carrying_cat(self):
        """Sprawdza czy gracz niesie kotka"""
        return self.carried_cat is not None

    def get_carried_cat(self):
        """Zwraca indeks noszonego kotka lub None"""
        return self.carried_cat

    def put_down_cat(self):
        """Odkłada kotka (do chatki). Zwraca indeks kotka lub None."""
        cat = self.carried_cat
        self.carried_cat = None
        return cat

    def add_collectible(self, collectible_index):
        """Dodaje znajdźkę do inventory"""
        self.collected_items.append(collectible_index)

    def get_collectible_count(self):
        """Zwraca liczbę zebranych znajdziek"""
        return len(self.collected_items)

    def set_storage_hint(self, show):
        """Ustawia czy pokazywać podpowiedź odkładania kotka"""
        self.show_storage_hint = show

    def update_inventory(self, keys, screen, stored_cats=0):
        # Zmienna do śledzenia, czy ekwipunek jest otwarty
        if keys[pygame.K_e] and not self.toggle_pressed:
            self.inventory_open = not self.inventory_open
            self.toggle_pressed = True

        if not keys[pygame.K_e]:
            self.toggle_pressed = False

        # Rysowanie ekwipunku, jeśli jest otwarty (tylko itemy!)
        if self.inventory_open:
            screen.blit(self.inventory_image, self.inventory_rect)
            self._draw_collected_items(screen)

        # Zawsze rysuj liczniki w rogu ekranu
        self._draw_counters(screen, stored_cats)

        # Rysuj wskaźnik noszonego kotka
        if self.carried_cat is not None:
            self._draw_carried_cat(screen)

        # Rysuj podpowiedź
        if self.show_collect_hint and self.carried_cat is None:
            self._draw_collect_hint(screen, "cat")
        elif self.show_collectible_hint:
            self._draw_collect_hint(screen, "item")
        elif self.show_storage_hint and self.carried_cat is not None:
            self._draw_collect_hint(screen, "storage")

    def _draw_carried_cat(self, screen):
        """Rysuje wskaźnik noszonego kotka w prawym górnym rogu"""
        if self.carried_cat is None:
            return

        padding = 10
        box_size = 60

        # Pozycja w prawym górnym rogu
        box_x = self.screen_width - box_size - padding
        box_y = padding

        # Tło ramki
        bg_rect = pygame.Rect(box_x, box_y, box_size, box_size)
        pygame.draw.rect(screen, (60, 50, 40), bg_rect, border_radius=8)
        pygame.draw.rect(screen, (255, 200, 100), bg_rect, 3, border_radius=8)

        # Obrazek kotka (bez napisu)
        cat_img = self.cat_images[self.carried_cat]
        cat_rect = cat_img.get_rect(center=(box_x + box_size // 2, box_y + box_size // 2))
        screen.blit(cat_img, cat_rect)

    def _draw_collected_items(self, screen):
        """Draw collected items in inventory"""
        if not self.collected_items:
            return

        # Parametry slotów
        slot_size = 50
        slots_per_row = 5
        start_x = self.inventory_rect.x + 80
        start_y = self.inventory_rect.y + 80

        for i, item_index in enumerate(self.collected_items):
            row = i // slots_per_row
            col = i % slots_per_row

            slot_x = start_x + col * (slot_size + 12)
            slot_y = start_y + row * (slot_size + 12)

            # Rysuj ramkę slotu
            slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)
            pygame.draw.rect(screen, (60, 70, 80), slot_rect, 3, border_radius=5)

            # Rysuj znajdźkę w slocie
            item_img = self.collectible_images[item_index]
            item_rect = item_img.get_rect(center=slot_rect.center)
            screen.blit(item_img, item_rect)

    def _draw_counters(self, screen, stored_cats=0):
        """Draw counters for cats and items in corner of screen"""
        padding = 6
        y_offset = 10

        # Cats counter (w chatce) - tylko liczba
        cat_text = f"{stored_cats}/5"
        cat_surface = self.font.render(cat_text, True, (255, 220, 150))

        cat_bg_rect = pygame.Rect(10, y_offset, cat_surface.get_width() + padding * 2, cat_surface.get_height() + padding * 2)
        pygame.draw.rect(screen, (50, 50, 50, 180), cat_bg_rect, border_radius=6)
        pygame.draw.rect(screen, (100, 80, 60), cat_bg_rect, 2, border_radius=6)
        screen.blit(cat_surface, (10 + padding, y_offset + padding))

        y_offset += cat_bg_rect.height + 5

        # Items counter - tylko liczba
        item_text = f"{len(self.collected_items)}/10"
        item_surface = self.font.render(item_text, True, (150, 200, 255))

        item_bg_rect = pygame.Rect(10, y_offset, item_surface.get_width() + padding * 2, item_surface.get_height() + padding * 2)
        pygame.draw.rect(screen, (50, 50, 50, 180), item_bg_rect, border_radius=6)
        pygame.draw.rect(screen, (60, 80, 100), item_bg_rect, 2, border_radius=6)
        screen.blit(item_surface, (10 + padding, y_offset + padding))

    def _draw_collect_hint(self, screen, item_type="cat"):
        """Draw hint for collecting cat or item"""
        if item_type == "cat":
            hint_text = "[F] Pick up cat"
        elif item_type == "storage":
            hint_text = "[G] Put cat on bed"
        else:
            hint_text = "[F] Collect item"

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
        """Ustawia czy pokazywać podpowiedź zbierania kota"""
        self.show_collect_hint = show

    def set_collectible_hint(self, show):
        """Ustawia czy pokazywać podpowiedź zbierania znajdźki"""
        self.show_collectible_hint = show
