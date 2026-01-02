import pygame
from src.ui.lore_display import create_placeholder
from src.ui.lore_data import CATS_LORE, COLLECTIBLES_LORE
from src.utils import get_image, get_font


def load_cat_images():
    """Load cat images for display (uses cache)"""
    cat_images = []
    for cat in CATS_LORE:
        if "image" in cat:
            cat_img = get_image(f'graphics/npc/{cat["image"]}', (50, 50))
            if cat_img is None:
                cat_img = create_placeholder((50, 50), cat["color"], cat["name"])
        else:
            cat_img = create_placeholder((50, 50), cat["color"], cat["name"])
        cat_images.append(cat_img)
    return cat_images


def load_collectible_images():
    """Load collectible images for inventory display (uses cache)"""
    coll_images = []
    for item in COLLECTIBLES_LORE:
        if "image" in item:
            coll_img = get_image(f'graphics/landscape/{item["image"]}', (40, 40))
            if coll_img is None:
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

        # Font do wyświetlania licznika (pixelowy) - uses cache
        self.font = get_font(12)
        self.small_font = get_font(8)
        self.title_font = get_font(14)
        self.lore_font = get_font(7)

        # Podpowiedź zbierania
        self.show_collect_hint = False
        self.show_collectible_hint = False
        self.hint_font = get_font(10)

        # System przechowywania w chatce
        self.show_storage_hint = False

        # Hover system
        self.hovered_item = None  # Index of hovered item or None
        self.slot_rects = []  # Will store slot rectangles for hover detection

        # Keyboard navigation system
        self.selected_slot = 0  # Currently selected slot (0-9)
        self.arrow_cooldown = 0  # Cooldown between arrow presses
        self.arrow_keys_pressed = {
            'up': False, 'down': False, 'left': False, 'right': False
        }

        # Coffee thermos system
        self.has_coffee = False
        self.show_coffee_hint = False
        self.coffee_hint_type = "brew"  # "brew" or "drink"

        # Fatigue bar animation
        self.fatigue_flash_timer = 0

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

    # Coffee thermos methods
    def fill_thermos(self):
        """Fill the coffee thermos."""
        self.has_coffee = True

    def drink_coffee(self):
        """Drink coffee from thermos. Returns True if had coffee."""
        if self.has_coffee:
            self.has_coffee = False
            return True
        return False

    def has_coffee_available(self):
        """Check if thermos has coffee."""
        return self.has_coffee

    def set_coffee_hint(self, show, hint_type="brew"):
        """Set coffee hint visibility and type."""
        self.show_coffee_hint = show
        self.coffee_hint_type = hint_type

    def update_inventory(self, keys, screen, stored_cats=0, fatigue=100):
        # Zmienna do śledzenia, czy ekwipunek jest otwarty
        if keys[pygame.K_e] and not self.toggle_pressed:
            self.inventory_open = not self.inventory_open
            self.toggle_pressed = True

        if not keys[pygame.K_e]:
            self.toggle_pressed = False

        # Rysowanie ekwipunku, jeśli jest otwarty (tylko itemy!)
        if self.inventory_open:
            # Handle keyboard navigation
            self._handle_keyboard_navigation(keys)

            # Dark overlay
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            self._draw_inventory_panel(screen)
            self._draw_collected_items(screen)
            self._check_hover()
            # Show tooltip for selected slot (keyboard) or hovered slot (mouse)
            active_slot = self.hovered_item if self.hovered_item is not None else self._get_selected_item_index()
            if active_slot is not None:
                self._draw_item_tooltip(screen, active_slot)

        # Zawsze rysuj liczniki w rogu ekranu
        self._draw_counters(screen, stored_cats, fatigue)

        # Rysuj wskaźnik noszonego kotka
        if self.carried_cat is not None:
            self._draw_carried_cat(screen)

        # Rysuj podpowiedź (coffee brew hint only - drink hint is shown in panel)
        if self.show_coffee_hint and self.coffee_hint_type == "brew":
            self._draw_collect_hint(screen, "coffee_brew")
        elif self.show_collect_hint and self.carried_cat is None:
            self._draw_collect_hint(screen, "cat")
        elif self.show_collectible_hint:
            self._draw_collect_hint(screen, "item")
        elif self.show_storage_hint and self.carried_cat is not None:
            self._draw_collect_hint(screen, "storage")
        elif self.carried_cat is not None:
            # Zawsze pokazuj info o niesieniu kotka gdy nie ma innych podpowiedzi
            self._draw_collect_hint(screen, "carry_cat")

    def _handle_keyboard_navigation(self, keys):
        """Handle arrow key navigation in inventory."""
        if self.arrow_cooldown > 0:
            self.arrow_cooldown -= 1
            return

        slots_per_row = 5
        moved = False

        # Left arrow
        if keys[pygame.K_LEFT] and not self.arrow_keys_pressed['left']:
            self.arrow_keys_pressed['left'] = True
            if self.selected_slot % slots_per_row > 0:
                self.selected_slot -= 1
                moved = True
        elif not keys[pygame.K_LEFT]:
            self.arrow_keys_pressed['left'] = False

        # Right arrow
        if keys[pygame.K_RIGHT] and not self.arrow_keys_pressed['right']:
            self.arrow_keys_pressed['right'] = True
            if self.selected_slot % slots_per_row < slots_per_row - 1:
                self.selected_slot += 1
                moved = True
        elif not keys[pygame.K_RIGHT]:
            self.arrow_keys_pressed['right'] = False

        # Up arrow
        if keys[pygame.K_UP] and not self.arrow_keys_pressed['up']:
            self.arrow_keys_pressed['up'] = True
            if self.selected_slot >= slots_per_row:
                self.selected_slot -= slots_per_row
                moved = True
        elif not keys[pygame.K_UP]:
            self.arrow_keys_pressed['up'] = False

        # Down arrow
        if keys[pygame.K_DOWN] and not self.arrow_keys_pressed['down']:
            self.arrow_keys_pressed['down'] = True
            if self.selected_slot < 10 - slots_per_row:
                self.selected_slot += slots_per_row
                moved = True
        elif not keys[pygame.K_DOWN]:
            self.arrow_keys_pressed['down'] = False

        if moved:
            self.arrow_cooldown = 8  # Short cooldown between moves
            self.hovered_item = None  # Clear mouse hover when using keyboard

    def _get_selected_item_index(self):
        """Get the item index at the selected slot, or None if empty."""
        if self.selected_slot < len(self.collected_items):
            return self.selected_slot
        return None

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

        # Rysuj wszystkie sloty (puste i z itemami)
        for i in range(10):
            row = i // slots_per_row
            col = i % slots_per_row

            slot_x = start_x + col * (slot_size + slot_spacing)
            slot_y = start_y + row * (slot_size + slot_spacing)

            slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)

            # Check if this slot is selected (keyboard) or hovered (mouse)
            is_selected = (i == self.selected_slot)
            is_hovered = (i < len(self.collected_items) and self.hovered_item == i)
            has_item = i < len(self.collected_items)

            # Draw slot background based on state
            if is_hovered:
                # Mouse hover - brightest highlight
                pygame.draw.rect(screen, (60, 55, 45), slot_rect, border_radius=5)
                pygame.draw.rect(screen, (200, 180, 120), slot_rect, 2, border_radius=5)
            elif is_selected:
                # Keyboard selection - yellow/gold border
                pygame.draw.rect(screen, (50, 45, 40), slot_rect, border_radius=5)
                pygame.draw.rect(screen, (255, 200, 100), slot_rect, 3, border_radius=5)
            else:
                # Normal slot
                pygame.draw.rect(screen, (35, 30, 25), slot_rect, border_radius=5)
                pygame.draw.rect(screen, (80, 70, 60), slot_rect, 2, border_radius=5)

            # Draw item if present
            if has_item:
                item_index = self.collected_items[i]
                self.slot_rects.append((slot_rect, item_index))
                item_img = self.collectible_images[item_index]
                item_rect = item_img.get_rect(center=slot_rect.center)
                screen.blit(item_img, item_rect)

        # Draw navigation hint at bottom of panel
        nav_hint = "Use arrows to navigate"
        nav_surface = self.small_font.render(nav_hint, True, (120, 110, 100))
        nav_x = self.panel_x + (self.panel_width - nav_surface.get_width()) // 2
        nav_y = self.panel_y + self.panel_height - 25
        screen.blit(nav_surface, (nav_x, nav_y))

    def _check_hover(self):
        """Sprawdza czy mysz jest nad którymś slotem"""
        mouse_pos = pygame.mouse.get_pos()
        self.hovered_item = None

        for i, (slot_rect, item_index) in enumerate(self.slot_rects):
            if slot_rect.collidepoint(mouse_pos):
                self.hovered_item = i
                break

    def _draw_item_tooltip(self, screen, active_slot=None):
        """Rysuje tooltip z nazwą i lore dla aktywnego slotu (hover lub selected)"""
        slot_to_show = active_slot if active_slot is not None else self.hovered_item
        if slot_to_show is None or slot_to_show >= len(self.collected_items):
            return

        item_index = self.collected_items[slot_to_show]
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

    def _draw_counters(self, screen, stored_cats=0, fatigue=100):
        """Draw counters: kittens/collectibles at top-left, energy/coffee at bottom-left"""
        padding = 6

        # ========== TOP-LEFT: Kittens and Collectibles ==========
        y_offset = 10

        # Kittens counter
        cat_text = f"{stored_cats}/5 Kittens"
        cat_surface = self.font.render(cat_text, True, (255, 220, 150))
        cat_bg_width = cat_surface.get_width() + padding * 2
        cat_bg_height = cat_surface.get_height() + padding * 2

        cat_bg_surface = pygame.Surface((cat_bg_width, cat_bg_height), pygame.SRCALPHA)
        pygame.draw.rect(cat_bg_surface, (50, 50, 50, 180), (0, 0, cat_bg_width, cat_bg_height), border_radius=6)
        pygame.draw.rect(cat_bg_surface, (100, 80, 60), (0, 0, cat_bg_width, cat_bg_height), 2, border_radius=6)
        screen.blit(cat_bg_surface, (10, y_offset))
        screen.blit(cat_surface, (10 + padding, y_offset + padding))

        y_offset += cat_bg_height + 5

        # Collectibles counter
        item_text = f"{len(self.collected_items)}/10 Collectibles"
        item_surface = self.font.render(item_text, True, (150, 200, 255))
        item_bg_width = item_surface.get_width() + padding * 2
        item_bg_height = item_surface.get_height() + padding * 2

        item_bg_surface = pygame.Surface((item_bg_width, item_bg_height), pygame.SRCALPHA)
        pygame.draw.rect(item_bg_surface, (50, 50, 50, 180), (0, 0, item_bg_width, item_bg_height), border_radius=6)
        pygame.draw.rect(item_bg_surface, (60, 80, 100), (0, 0, item_bg_width, item_bg_height), 2, border_radius=6)
        screen.blit(item_bg_surface, (10, y_offset))
        screen.blit(item_surface, (10 + padding, y_offset + padding))

        # ========== BOTTOM-LEFT: Coffee Energy Panel ==========
        margin = 15
        panel_width = 180
        panel_height = 95
        panel_x = margin
        panel_y = self.screen_height - margin - panel_height

        # Panel background with proper rounded corners
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (30, 30, 30, 200), (0, 0, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(panel_surface, (80, 70, 60), (0, 0, panel_width, panel_height), 2, border_radius=10)
        screen.blit(panel_surface, (panel_x, panel_y))

        current_y = panel_y + 8

        # === COFFEE ENERGY LABEL ===
        energy_label = self.small_font.render("Coffee Energy", True, (180, 160, 120))
        screen.blit(energy_label, (panel_x + 8, current_y))
        current_y += energy_label.get_height() + 4

        bar_width = panel_width - 16
        bar_height = 14
        bar_x = panel_x + 8
        bar_y = current_y

        # Energy bar with proper rounded corners
        bar_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        pygame.draw.rect(bar_surface, (40, 40, 40), (0, 0, bar_width, bar_height), border_radius=4)

        # Fill color based on fatigue
        if fatigue > 50:
            fill_color = (139, 90, 43)
        elif fatigue > 20:
            fill_color = (180, 100, 30)
        else:
            self.fatigue_flash_timer += 1
            if self.fatigue_flash_timer % 30 < 15:
                fill_color = (200, 50, 50)
            else:
                fill_color = (140, 40, 40)

        fill_width = int((bar_width * fatigue) / 100)
        if fill_width > 0:
            pygame.draw.rect(bar_surface, fill_color, (0, 0, fill_width, bar_height), border_radius=4)

        pygame.draw.rect(bar_surface, (100, 80, 60), (0, 0, bar_width, bar_height), 2, border_radius=4)
        screen.blit(bar_surface, (bar_x, bar_y))

        current_y += bar_height + 10

        # === COFFEE CUP ===
        cup_x = panel_x + 8
        cup_y = current_y
        cup_bg_width = 44
        cup_bg_height = 36

        # Cup background with proper rounded corners
        cup_surface = pygame.Surface((cup_bg_width, cup_bg_height), pygame.SRCALPHA)
        pygame.draw.rect(cup_surface, (50, 45, 40), (0, 0, cup_bg_width, cup_bg_height), border_radius=6)
        screen.blit(cup_surface, (cup_x, cup_y))

        mug_x = cup_x + 6
        mug_y = cup_y + 4
        pygame.draw.rect(screen, (120, 90, 60), (mug_x, mug_y + 6, 24, 22), border_radius=3)
        pygame.draw.arc(screen, (120, 90, 60), (mug_x + 22, mug_y + 10, 10, 14), -1.5, 1.5, 3)

        if self.has_coffee:
            pygame.draw.rect(screen, (70, 45, 25), (mug_x + 3, mug_y + 10, 18, 14), border_radius=2)
            pygame.draw.line(screen, (220, 220, 220), (mug_x + 8, mug_y + 4), (mug_x + 6, mug_y - 2), 2)
            pygame.draw.line(screen, (220, 220, 220), (mug_x + 16, mug_y + 4), (mug_x + 18, mug_y - 3), 2)
            pygame.draw.rect(screen, (180, 140, 80), (cup_x, cup_y, cup_bg_width, cup_bg_height), 2, border_radius=6)
        else:
            pygame.draw.rect(screen, (60, 60, 60), (cup_x, cup_y, cup_bg_width, cup_bg_height), 2, border_radius=6)

        label_x = cup_x + cup_bg_width + 8
        if self.has_coffee:
            coffee_label = self.small_font.render("Ready!", True, (180, 140, 80))
            screen.blit(coffee_label, (label_x, cup_y + 2))
            hint_surface = self.hint_font.render("[V] Drink", True, (255, 220, 150))
            screen.blit(hint_surface, (label_x, cup_y + 18))
        else:
            coffee_label = self.small_font.render("Empty", True, (120, 120, 120))
            screen.blit(coffee_label, (label_x, cup_y + 10))

    def _draw_collect_hint(self, screen, item_type="cat"):
        """Draw hint for collecting cat or item"""
        if item_type == "cat":
            hint_text = "[F] Pick up cat"
        elif item_type == "storage":
            hint_text = "[G] Put cat on bed"
        elif item_type == "carry_cat":
            hint_text = "Bring the cat to the cabin!"
        elif item_type == "coffee_brew":
            hint_text = "[C] Brew coffee"
        elif item_type == "coffee_drink":
            hint_text = "[V] Drink coffee"
        elif item_type == "item":
            hint_text = "[F] Collect item"
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
