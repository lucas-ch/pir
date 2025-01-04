import pygame
import os
from settings import *
from task import *

class Dropdown:
    def __init__(self,
                 title: str,
                 x: int,
                 y: int,
                 w: int,
                 total_height: int,
                 font: pygame.font.Font,
                 main: str,
                 options: list[str],
                 event: str):
        self.color = 'White'
        self.bg_color = (0, 200, 0)
        self.highlight_color = (100, 255, 100)  # Highlight color for hovered options
        self.font = font
        self.main = main
        self.options = options
        self.selected = main
        self.active = False
        self.options_rect: list = []
        self.event = event
        self.title = title

        # Calculate title height
        title_msg = self.font.render(self.title, True, self.color)
        self.title_height = title_msg.get_height()

        # Adjust rectangle height to fit the total height
        rect_height = total_height - self.title_height

        # Define the dropdown rectangle
        self.rect = pygame.Rect(x, y + self.title_height, w, rect_height)
        self.title_x = x  # Title alignment with the rect

    def input(self):
        mouse_pressed = pygame.mouse.get_just_pressed()
        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            if mouse_pressed[0]:  # Left mouse button clicked
                self.active = not self.active

        for e in self.options_rect:
            if e["rect"].collidepoint(mouse_pos):
                if mouse_pressed[0]:  # Select option on click
                    self.selected = e["text"]
                    pygame.event.post(pygame.event.Event(self.event, {"value": e["text"]}))
                    self.active = False

    def draw(self, surface: pygame.Surface):
        # Render the title text
        title_msg = self.font.render(self.title, True, 'Black')
        title_rect = title_msg.get_rect(topleft=(self.title_x, self.rect.top - self.title_height))
        surface.blit(title_msg, title_rect)

        # Render the dropdown rectangle
        pygame.draw.rect(surface, self.bg_color, self.rect)
        msg = self.font.render(self.selected, True, self.color)
        surface.blit(msg, msg.get_rect(center=self.rect.center))

        # Render the dropdown options if active
        self.options_rect = []
        if self.active:
            mouse_pos = pygame.mouse.get_pos()
            for i, option in enumerate(self.options):
                rect = self.rect.copy()
                rect.y += (i + 1) * self.rect.height

                # Highlight the option if the mouse is hovering over it
                if rect.collidepoint(mouse_pos):
                    pygame.draw.rect(surface, self.highlight_color, rect)
                else:
                    pygame.draw.rect(surface, self.bg_color, rect)

                msg = self.font.render(option, True, self.color)
                surface.blit(msg, msg.get_rect(center=rect.center))
                self.options_rect.append({"text": option, "rect": rect})
