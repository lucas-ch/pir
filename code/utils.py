from settings import *
import pygame
from enum import Enum

class EventsEnum(Enum):
    TASK_ASSIGNED_CLICKED = pygame.USEREVENT + 1
    START_CLICKED = pygame.USEREVENT + 2 
    METHOD_CHANGED = pygame.USEREVENT + 3
    RETRY_CLICKED = pygame.USEREVENT + 4

def convert_coordinates_to_tile(coordinates: pygame.Rect | pygame.FRect):
    return {
        "x": int(coordinates.x / TILE_SIZE),
        "y": int(coordinates.y / TILE_SIZE)
    }