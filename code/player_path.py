import pygame
from player import Player
from settings import *

class PlayerPath(pygame.sprite.Sprite):
    def __init__(self, player: Player, groups: list[pygame.sprite.Group]):
        super().__init__(groups)
        self.player = player

    def update(self, surface):
        """Dessine le chemin du joueur sur la surface donnée."""
        if not self.player.planned_path:
            return

        for path in self.player.planned_path:
            if len(path) > 1:
                real_path = [(node.x * TILE_SIZE + TILE_SIZE // 2,  
                              node.y * TILE_SIZE + TILE_SIZE // 2) for node in path]
                pygame.draw.lines(surface, self.player.color, False, real_path, 3)
