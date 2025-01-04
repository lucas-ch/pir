import pygame

class Button:
    def __init__(self,
                 left:int,
                 top:int,
                 width:int,
                 height:int,
                 color:str,
                 text:str,
                 event:int,
                 font:pygame.font.Font,
                 disabled:bool):
        self.color = color
        self.disabled = disabled
        self.rect = pygame.Rect(left, top, width, height)
        self.text = text
        self.event=event
        self.clicked = False
        self.font = font
        self.hidden = False

    def input(self):
            mouse_pressed = pygame.mouse.get_just_released()
            mouse_pos = pygame.mouse.get_pos()

            if self.rect.collidepoint(mouse_pos) and not self.disabled:
                if mouse_pressed[0]:
                    self.clicked = True
                elif self.clicked:
                    self.clicked = False
                    pygame.event.post(pygame.event.Event(self.event))

    def draw(self, surface:pygame.Surface):
        if self.hidden:
            return

        mouse_pos = pygame.mouse.get_pos()

        is_hovered = self.rect.collidepoint(mouse_pos)
        is_clicked = self.clicked
        base_color = (150, 150, 150) if self.disabled else self.color
        hover_color = (min(base_color[0] + 50, 255), min(base_color[1] + 50, 255), min(base_color[2] + 50, 255))
        clicked_color = (max(base_color[0] - 50, 0), max(base_color[1] - 50, 0), max(base_color[2] - 50, 0))

        if is_clicked:
            color = clicked_color
        elif is_hovered and not self.disabled:
            color = hover_color
        else:
            color = base_color

        # Draw button rectangle
        pygame.draw.rect(surface, color, self.rect)

        # Draw button text
        text_surf = self.font.render(self.text, False, 'White' if not self.disabled else 'Gray')
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
