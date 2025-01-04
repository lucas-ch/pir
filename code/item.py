from settings import *
import pygame

class Item(pygame.sprite.Sprite):
    _id_counter = 0
    
    def __init__(self, type:str, pos, surf:pygame.Surface, groups:list[pygame.sprite.Group]):
        super().__init__(groups)

        self.id = Item._id_counter
        Item._id_counter += 1

        self.type = type

        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.current_health = 100

    @classmethod
    def reset_counter(cls):
        Item._id_counter = 0

    def decrease_health(self, amount):
        """Decrease the health of the item."""
        self.current_health = max(0, self.current_health - amount)

        if self.current_health == 0:
            self.kill()
