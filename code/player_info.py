import pygame
import os
from player import Player

class PlayerInfo(pygame.sprite.Sprite):
    def __init__(self, player:Player, groups:list[pygame.sprite.Group]):
        super().__init__(groups)  # Initialize the sprite and add to groups if provided
        self.player = player
        self.font = pygame.font.Font(os.path.join('font', 'LycheeSoda.ttf'), 20)
        self.color = 'Black'

        # Create a surface for rendering the player ID
        self.image = pygame.Surface((player.rect.width, 20), pygame.SRCALPHA)  # Transparent background
        self.rect = self.image.get_rect(midbottom=player.rect.midtop)  # Position above the player

    def update(self, *args):
        # Update the position of the ID display to follow the player
        self.rect.midbottom = self.player.rect.midtop

        # Render the ID onto the surface
        self.image.fill((0, 0, 0, 0))  # Clear the surface (transparent)
        id_text_surf = self.font.render(str(self.player.id), True, self.color)
        id_text_rect = id_text_surf.get_rect(center=self.image.get_rect().center)
        self.image.blit(id_text_surf, id_text_rect)
