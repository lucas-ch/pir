import pygame
from task import Task

class Table:
    def __init__(self,
                 width:int,
                 row_height:int,
                 columns:list[str],
                 columns_width:list[int],
                 tasks:list[Task],
                 font:pygame.font.Font):
        self.width = width
        self.row_height = row_height
        self.columns  = columns
        self.columns_width = columns_width
        self.tasks = tasks
        self.font = font
        self.text_surfs = []

    def setup(self):
        # Render headers
        self.header_surfs = [self.font.render(header, False, 'Black') for header in self.columns]

        # Render task data
        self.text_surfs = []
        for task in self.tasks:
            row = [
                self.font.render(str(task.type), False, 'Black'),
                self.font.render(str(task.item.id), False, 'Black'),
                self.font.render(str(task.status), False, 'Black'),
                self.font.render(str(task.assigned_to), False, 'Black'),
                self.font.render(str(task.utility), False, 'Black'),
            ]
            self.text_surfs.append(row)
    
    def draw(self, surface:pygame.Surface, x_start:int, y_start:int):
        self.setup()
        # Draw headers
        y_offset = self.row_height  # Offset between rows

        # Draw header row
        x = x_start
        for i, header_surf in enumerate(self.header_surfs):
            surface.blit(header_surf, (x, y_start))
            x += self.columns_width[i]

        # Draw tasks
        for row_index, row in enumerate(self.text_surfs):
            x = x_start
            for col_index, cell_surf in enumerate(row):
                surface.blit(cell_surf, (x, y_start + (row_index + 1) * y_offset))
                x += self.columns_width[col_index]
