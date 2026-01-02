import pygame
from src.utils import get_font


class TutorialSystem:
    """System showing tutorial hints for first-time players."""

    # Tutorial steps
    STEP_TALK_TO_SPRYTEK = 0
    STEP_BREW_COFFEE = 1
    STEP_OPEN_INVENTORY = 2
    STEP_FIND_CATS = 3
    STEP_COMPLETED = 4

    TUTORIAL_TEXTS = {
        STEP_TALK_TO_SPRYTEK: {
            "title": "Welcome!",
            "text": "Talk to Sprytek [F] and listen to his story.",
            "hint": "Approach the character in front of the cabin",
        },
        STEP_BREW_COFFEE: {
            "title": "Coffee Time",
            "text": "Go inside the cabin and brew coffee [C].",
            "hint": "The coffee machine is inside the cabin",
        },
        STEP_OPEN_INVENTORY: {
            "title": "Inventory",
            "text": "Open your inventory [E] to see collected items.",
            "hint": "Use arrows to navigate items",
        },
        STEP_FIND_CATS: {
            "title": "Your Quest",
            "text": "Find kittens [F] and bring them to the cabin [G].",
            "hint": "Press [F] to start",
        },
    }

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_step = self.STEP_TALK_TO_SPRYTEK
        self.is_active = False

        # Fonts
        self.title_font = get_font(14)
        self.text_font = get_font(10)
        self.hint_font = get_font(8)

        # UI dimensions
        self.box_width = 500
        self.box_height = 120
        self.box_x = (screen_width - self.box_width) // 2
        self.box_y = 20

        # Animation
        self.fade_alpha = 0
        self.fade_in = True

        # Input handling
        self.f_key_pressed = False
        self.cooldown = 0

        # Track if certain actions happened
        self.talked_to_sprytek_complete = False
        self.coffee_brewed = False
        self.inventory_opened = False

    def start(self):
        """Start the tutorial from the beginning."""
        self.is_active = True
        self.current_step = self.STEP_TALK_TO_SPRYTEK
        self.fade_alpha = 0
        self.fade_in = True
        self.talked_to_sprytek_complete = False
        self.coffee_brewed = False
        self.inventory_opened = False

    def stop(self):
        """Stop the tutorial."""
        self.is_active = False
        self.current_step = self.STEP_COMPLETED

    def is_completed(self):
        """Check if tutorial is completed."""
        return self.current_step >= self.STEP_COMPLETED

    def update(self, keys, npc=None, inventory=None):
        """Update tutorial state based on player actions."""
        if not self.is_active or self.is_completed():
            return

        # Handle cooldown
        if self.cooldown > 0:
            self.cooldown -= 1

        # Update fade animation
        if self.fade_in:
            self.fade_alpha = min(255, self.fade_alpha + 10)
        else:
            self.fade_alpha = max(0, self.fade_alpha - 10)

        # Check step completion
        if self.current_step == self.STEP_TALK_TO_SPRYTEK:
            # Complete when player has talked through quest_intro dialog (now index 0)
            if npc and npc.current_dialog_index >= 1:
                self.talked_to_sprytek_complete = True
            if self.talked_to_sprytek_complete and (npc is None or not npc.is_talking):
                self._advance_step()

        elif self.current_step == self.STEP_BREW_COFFEE:
            # Complete when coffee is brewed
            if inventory and inventory.has_coffee_available():
                self.coffee_brewed = True
                self._advance_step()

        elif self.current_step == self.STEP_OPEN_INVENTORY:
            # Complete when inventory is opened
            if inventory and inventory.inventory_open:
                self.inventory_opened = True
            if self.inventory_opened and (inventory is None or not inventory.inventory_open):
                self._advance_step()

        elif self.current_step == self.STEP_FIND_CATS:
            # Manual advance with F key
            if keys[pygame.K_f] and not self.f_key_pressed and self.cooldown == 0:
                self.f_key_pressed = True
                self.cooldown = 15
                self._advance_step()

        if not keys[pygame.K_f]:
            self.f_key_pressed = False

    def _advance_step(self):
        """Move to next tutorial step."""
        self.current_step += 1
        self.fade_alpha = 0
        self.fade_in = True

        if self.current_step >= self.STEP_COMPLETED:
            self.is_active = False

    def draw(self, screen):
        """Draw current tutorial hint."""
        if not self.is_active or self.is_completed():
            return

        if self.current_step not in self.TUTORIAL_TEXTS:
            return

        step_data = self.TUTORIAL_TEXTS[self.current_step]

        # Create surface with alpha
        box_surface = pygame.Surface((self.box_width, self.box_height), pygame.SRCALPHA)

        # Background
        bg_alpha = int(200 * (self.fade_alpha / 255))
        pygame.draw.rect(box_surface, (30, 30, 40, bg_alpha),
                        (0, 0, self.box_width, self.box_height), border_radius=12)

        # Border
        border_alpha = int(255 * (self.fade_alpha / 255))
        pygame.draw.rect(box_surface, (180, 150, 100, border_alpha),
                        (0, 0, self.box_width, self.box_height), 3, border_radius=12)

        # Inner border
        pygame.draw.rect(box_surface, (100, 80, 60, border_alpha),
                        (4, 4, self.box_width - 8, self.box_height - 8), 2, border_radius=10)

        screen.blit(box_surface, (self.box_x, self.box_y))

        if self.fade_alpha < 100:
            return

        # Title
        title_color = (255, 220, 150, self.fade_alpha)
        title_surface = self.title_font.render(step_data["title"], True, title_color[:3])
        title_surface.set_alpha(self.fade_alpha)
        title_x = self.box_x + (self.box_width - title_surface.get_width()) // 2
        screen.blit(title_surface, (title_x, self.box_y + 12))

        # Main text
        text_color = (230, 230, 230)
        text_surface = self.text_font.render(step_data["text"], True, text_color)
        text_surface.set_alpha(self.fade_alpha)
        text_x = self.box_x + (self.box_width - text_surface.get_width()) // 2
        screen.blit(text_surface, (text_x, self.box_y + 40))

        # Hint text
        hint_color = (150, 140, 120)
        hint_surface = self.hint_font.render(step_data["hint"], True, hint_color)
        hint_surface.set_alpha(self.fade_alpha)
        hint_x = self.box_x + (self.box_width - hint_surface.get_width()) // 2
        screen.blit(hint_surface, (hint_x, self.box_y + 70))

        # Step indicator
        step_text = f"Step {self.current_step + 1}/4"
        step_surface = self.hint_font.render(step_text, True, (100, 100, 100))
        step_surface.set_alpha(self.fade_alpha)
        screen.blit(step_surface, (self.box_x + 10, self.box_y + self.box_height - 20))
