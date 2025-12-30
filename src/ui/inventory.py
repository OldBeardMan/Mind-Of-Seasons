import pygame
from src.ui.lore_display import create_placeholder
from src.ui.lore_data import CATS_LORE, COLLECTIBLES_LORE
from src.utils import resource_path


def load_cat_images():
    """Ładuje obrazki kotków do wyświetlania"""
    cat_images = []
    for cat in CATS_LORE:
        if "image" in cat:
            try:
                cat_img = pygame.image.load(resource_path(f'Grafiki/NPC/{cat["image"]}')).convert_alpha()
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
                coll_img = pygame.image.load(resource_path(f'Grafiki/Landscape/{item["image"]}')).convert_alpha()
                coll_img = pygame.transform.scale(coll_img, (40, 40))
            except:
                coll_img = create_placeholder((40, 40), item["color"], item["name"])
        else:
            coll_img = create_placeholder((40, 40), item["color"], item["name"])
        coll_images.append(coll_img)
    return coll_images


class Inventory:
    def __init__(self, screen_width, screen_height):
        self.inventory_open = False
        self.toggle_pressed = False
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Rozmiary panelu inventory
        self.panel_width = 400
        self.panel_height = 350
        self.panel_x = (screen_width - self.panel_width) // 2
        self.panel_y = (screen_height - self.panel_height) // 2
        self.panel_color = (45, 40, 35)
        self.panel_border_color = (180, 160, 120)

        # Obrazki kotków (do wyświetlania noszonego kotka)
        self.cat_images = load_cat_images()

        # Lista zebranych znajdziek (tylko itemy, nie kotki!)
        self.collected_items = []
        self.collectible_images = load_collectible_images()

        # System noszenia kotka na rękach (tylko jeden naraz!)
        self.carried_cat = None  # Indeks noszonego kotka lub None

        # Font do wyświetlania licznika (pixelowy)
        pygame.font.init()
        self.font = pygame.font.Font(resource_path('Czcionki/PressStart2P.ttf'), 12)
        self.small_font = pygame.font.Font(resource_path('Czcionki/PressStart2P.ttf'), 8)
        self.title_font = pygame.font.Font(resource_path('Czcionki/PressStart2P.ttf'), 14)
        self.lore_font = pygame.font.Font(resource_path('Czcionki/PressStart2P.ttf'), 7)

        # Podpowiedź zbierania
        self.show_collect_hint = False
        self.show_collectible_hint = False
        self.hint_font = pygame.font.Font(resource_path('Czcionki/PressStart2P.ttf'), 10)

        # System przechowywania w chatce
        self.show_storage_hint = False

        # Hover system
        self.hovered_item = None  # Index of hovered item or None
        self.slot_rects = []  # Will store slot rectangles for hover detection

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
            self._draw_inventory_panel(screen)
            self._draw_collected_items(screen)
            self._check_hover()
            if self.hovered_item is not None:
                self._draw_item_tooltip(screen)

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
        elif self.carried_cat is not None:
            # Zawsze pokazuj info o niesieniu kotka gdy nie ma innych podpowiedzi
            self._draw_collect_hint(screen, "carry_cat")

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

    def _draw_inventory_panel(self, screen):
        """Rysuje panel inventory (prostokątny, jak dymek Sprytka)"""
        # Tło panelu
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        pygame.draw.rect(screen, self.panel_color, panel_rect, border_radius=12)
        pygame.draw.rect(screen, self.panel_border_color, panel_rect, 3, border_radius=12)

        # Tytuł
        title_text = "Inventory"
        title_surface = self.title_font.render(title_text, True, (230, 220, 200))
        title_x = self.panel_x + (self.panel_width - title_surface.get_width()) // 2
        screen.blit(title_surface, (title_x, self.panel_y + 15))

        # Linia pod tytułem
        line_y = self.panel_y + 45
        pygame.draw.line(screen, self.panel_border_color,
                        (self.panel_x + 20, line_y),
                        (self.panel_x + self.panel_width - 20, line_y), 2)

    def _draw_collected_items(self, screen):
        """Draw collected items in inventory"""
        self.slot_rects = []  # Reset slot rects for hover detection

        # Parametry slotów
        slot_size = 50
        slots_per_row = 5
        slot_spacing = 12
        start_x = self.panel_x + (self.panel_width - (slots_per_row * slot_size + (slots_per_row - 1) * slot_spacing)) // 2
        start_y = self.panel_y + 60

        # Rysuj puste sloty
        for i in range(10):
            row = i // slots_per_row
            col = i % slots_per_row

            slot_x = start_x + col * (slot_size + slot_spacing)
            slot_y = start_y + row * (slot_size + slot_spacing)

            slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)

            # Tło slotu
            pygame.draw.rect(screen, (35, 30, 25), slot_rect, border_radius=5)
            pygame.draw.rect(screen, (80, 70, 60), slot_rect, 2, border_radius=5)

        # Rysuj zebrane itemy
        for i, item_index in enumerate(self.collected_items):
            row = i // slots_per_row
            col = i % slots_per_row

            slot_x = start_x + col * (slot_size + slot_spacing)
            slot_y = start_y + row * (slot_size + slot_spacing)

            slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)
            self.slot_rects.append((slot_rect, item_index))

            # Podświetlenie przy hover
            if self.hovered_item == i:
                pygame.draw.rect(screen, (60, 55, 45), slot_rect, border_radius=5)
                pygame.draw.rect(screen, (200, 180, 120), slot_rect, 2, border_radius=5)
            else:
                pygame.draw.rect(screen, (35, 30, 25), slot_rect, border_radius=5)
                pygame.draw.rect(screen, (80, 70, 60), slot_rect, 2, border_radius=5)

            # Rysuj znajdźkę w slocie
            item_img = self.collectible_images[item_index]
            item_rect = item_img.get_rect(center=slot_rect.center)
            screen.blit(item_img, item_rect)

    def _check_hover(self):
        """Sprawdza czy mysz jest nad którymś slotem"""
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_item = None

        for i, (slot_rect, item_index) in enumerate(self.slot_rects):
            if slot_rect.collidepoint(mouse_pos):
                self.hovered_item = i
                break

    def _draw_item_tooltip(self, screen):
        """Rysuje tooltip z nazwą i lore dla hovera nad itemem"""
        if self.hovered_item is None or self.hovered_item >= len(self.collected_items):
            return

        item_index = self.collected_items[self.hovered_item]
        item_data = COLLECTIBLES_LORE[item_index]

        # Tooltip w dolnej części panelu
        tooltip_x = self.panel_x + 20
        tooltip_y = self.panel_y + 190
        tooltip_width = self.panel_width - 40

        # Nazwa itemu
        name_surface = self.font.render(item_data["name"], True, (255, 220, 150))
        screen.blit(name_surface, (tooltip_x, tooltip_y))

        # Lore (pierwsza linia lub więcej)
        lore_y = tooltip_y + 25
        text_color = (180, 170, 150)
        max_width = tooltip_width

        for lore_line in item_data["lore"][:3]:  # Max 3 linie lore
            # Łamanie tekstu
            words = lore_line.split(' ')
            current_line = ""

            for word in words:
                test_line = current_line + word + " "
                test_surface = self.lore_font.render(test_line, True, text_color)
                if test_surface.get_width() <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        line_surface = self.lore_font.render(current_line.strip(), True, text_color)
                        screen.blit(line_surface, (tooltip_x, lore_y))
                        lore_y += 14
                    current_line = word + " "

            if current_line:
                line_surface = self.lore_font.render(current_line.strip(), True, text_color)
                screen.blit(line_surface, (tooltip_x, lore_y))
                lore_y += 14

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
        elif item_type == "carry_cat":
            hint_text = "Bring the cat to the cabin!"
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
