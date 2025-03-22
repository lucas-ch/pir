import pygame
import os
from player import Player

class PlayerInfo(pygame.sprite.Sprite):
    def __init__(self, player: Player, groups: list[pygame.sprite.Group]):
        super().__init__(groups)  
        self.player = player
        self.font = pygame.font.Font(os.path.join('font', 'LycheeSoda.ttf'), 30)
        self.color = 'Black'

        # Définition des dimensions de la barre
        self.bar_width = player.rect.width
        self.bar_height = 5  # Hauteur de la barre colorée

        # Création de l'image avec de la transparence
        self.image = pygame.Surface((self.bar_width, 25), pygame.SRCALPHA)  
        self.rect = self.image.get_rect(midbottom=player.rect.midtop)  

    def update(self, *args):
        # Met à jour la position au-dessus du joueur
        self.rect.midbottom = self.player.rect.midtop

        # Efface la surface en la remplissant de transparent
        self.image.fill((0, 0, 0, 0))  

        # Dessine la barre colorée
        pygame.draw.rect(self.image, self.player.color, (0, 0, self.bar_width, self.bar_height))

        # Affichage de l'ID du joueur
        id_text_surf = self.font.render(str(self.player.id), True, self.color)
        id_text_rect = id_text_surf.get_rect(center=(self.bar_width // 2, self.bar_height + 10))
        self.image.blit(id_text_surf, id_text_rect)
