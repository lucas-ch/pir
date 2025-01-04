from settings import * 
import pygame

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos:tuple[int], surf:pygame.Surface, groups:list[pygame.sprite.Group]):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
