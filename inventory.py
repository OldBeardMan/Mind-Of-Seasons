
    # TODO Zaprogramować UI, przyciski otwarcia inventory, wyświetlanie inventory, dodawanie kotków po kliknięciu do inventory
import pygame
def load_inventory_graphics():
    image_inventory = pygame.image.load('Grafiki/UI/Slot.png').convert_alpha()
    image_inventory = pygame.transform.scale(image_inventory,(700,900))
    return image_inventory

class Inventory:
    def __init__(self,screen_width, screen_height):
        # Ładowanie grafiki ekwipunku
        self.inventory_image = load_inventory_graphics()
        self.inventory_rect = self.inventory_image.get_rect(center=(screen_width // 2, screen_height // 2))
        self.inventory_open = False
        self.toggle_pressed = False

    def update_inventory(self,keys,screen):
        # Zmienna do śledzenia, czy ekwipunek jest otwarty
        if keys[pygame.K_e] and not self.toggle_pressed:
            self.inventory_open = not self.inventory_open  # Przełącz stan ekwipunku
            self.toggle_pressed = True  # Zablokuj przełącznik, dopóki klawisz 'E' nie zostanie zwolniony

            # Zresetuj przełącznik po zwolnieniu klawisza 'E'
        if not keys[pygame.K_e]:
            self.toggle_pressed = False

            # Rysowanie ekwipunku, jeśli jest otwarty
        if self.inventory_open:
            screen.blit(self.inventory_image, self.inventory_rect)