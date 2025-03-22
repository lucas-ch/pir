import pygame
import os
from item import Item

class ItemInfo(pygame.sprite.Sprite):
    def __init__(self, item: Item, groups:list[pygame.sprite.Group]):
        super().__init__(groups)  # Initialize the sprite and add to groups if provided
        self.item = item
        self.font = pygame.font.Font(os.path.join('font', 'LycheeSoda.ttf'), 30)
        self.color = 'Black'

        # Health attributes
        self.max_health = 100
        self.health_bar_width = 50
        self.health_bar_height = 5
        self.health_bar_color = item.color

        # Create a surface for rendering the item info
        self.image = pygame.Surface((max(item.rect.width, self.health_bar_width), 40), pygame.SRCALPHA)  # Transparent background
        self.rect = self.image.get_rect(midbottom=item.rect.midtop)  # Position above the item

    def update(self, *args):
        if not self.item.alive():
            self.image.fill((0, 0, 0, 0))
            return

        # Update the position of the info display to follow the item
        self.rect.midbottom = self.item.rect.midtop

        # Clear the surface (transparent)
        self.image.fill((0, 0, 0, 0))

        # Render the health bar
        health_ratio = self.item.current_health / self.max_health
        current_health_width = int(self.health_bar_width * health_ratio)
        self.health_bar_color = self.item.color
        pygame.draw.rect(self.image, (255, 0, 0), (0, 0, self.health_bar_width, self.health_bar_height))  # Red background
        pygame.draw.rect(self.image, self.health_bar_color, (0, 0, current_health_width, self.health_bar_height))  # Green foreground

        # Render the ID text
        id_text_surf = self.font.render(str(self.item.id), True, self.color)
        id_text_rect = id_text_surf.get_rect(center=(self.image.get_width() // 2, self.health_bar_height + 10))
        self.image.blit(id_text_surf, id_text_rect)
