import pygame
import os
from settings import *
from task import *
from dropdown import *
from button import *
from table import *
from utils import *
from planner import *

class Menu:
    def __init__(self, display_menu:bool, tasks: list[Task], assignement_method: str):
        self.display_menu = display_menu

        # general stuff
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(os.path.join('font', 'LycheeSoda.ttf'), 15)

        self.padding = 5
        self.background_height = 0  # Will be calculated dynamically
        self.x_start = self.padding * 4
        self.y_start = self.padding * 4
        self.backgroung_color = (255, 255, 255, 200)

        # Dropdowns
        methods = [method.name for method in list(AssignMethodsEnum)]

        self.dropdown_height = 50
        self.dropdown_width = 150
        self.dropdowns = [
            Dropdown(
                "Methods",
                self.x_start,
                self.y_start,
                self.dropdown_width,
                self.dropdown_height,
                self.font,
                assignement_method,
                methods,
                EventsEnum.METHOD_CHANGED.value)
        ]

        # table dimensions
        self.width = 600
        self.row_height = 20

        # table content
        self.tasks = tasks
        self.headers = ["Type", "Item", "Status", "Robot", "Utility"]
        self.column_widths = [70, 80, 80, 70, 80]
        self.background_width = sum(self.column_widths)
        self.table = Table(self.width, self.row_height, self.headers, self.column_widths, self.tasks, self.font)

        # Buttons
        self.button_width = 100
        self.button_height = 30
        self.buttons = [
            Button(
                0,
                0,
                self.button_width,
                self.button_height,
                (0, 200, 0),
                "Assign Tasks",
                EventsEnum.TASK_ASSIGNED_CLICKED.value,
                self.font,
                False),
            Button(
                0,
                0,
                self.button_width,
                self.button_height,
                (0, 200, 0),
                "Start Tasks", EventsEnum.START_CLICKED.value,
                self.font,
                True),
            Button(
                0,
                0,
                self.button_width,
                self.button_height,
                (0, 200, 0),
                "Retry", EventsEnum.RETRY_CLICKED.value,
                self.font,
                False),
        ]

        self.display_compute = False
        self.game_started = False
        self.enable_start = False
        self.display_retry = False

    def toggle_menu(self):
        self.display_menu = not self.display_menu

    def input(self):
        keys = pygame.key.get_just_pressed()
        if keys[pygame.K_m]:
            self.toggle_menu()

        for button in self.buttons:
            button.input()

        for dropdown in self.dropdowns:
            dropdown.input()

    def draw_table(self):
        self.table.tasks = self.tasks
        
        # Create a semi-transparent background surface
        num_rows = len(self.tasks) + 1
        self.background_height = self.row_height * num_rows + self.padding * 2
        background = pygame.Surface((self.background_width, self.background_height), pygame.SRCALPHA)
        background.fill(self.backgroung_color)  # White with transparency (200/255)

        # Blit the background at a fixed position
        y_start = self.y_start + 2 * self.padding + self.dropdown_height
        self.display_surface.blit(background, (self.x_start - self.padding, y_start))

        self.table.draw(self.display_surface, self.x_start, y_start + self.padding)

    def draw_buttons(self):
        # background surface for buttons
        background_button = pygame.Surface((self.background_width, self.button_height + 2 * self.padding), pygame.SRCALPHA)
        background_button.fill(self.backgroung_color)  # White with transparency (200/255)

        y_start = self.y_start + 3 * self.padding + self.dropdown_height + self.background_height
        self.display_surface.blit(background_button, (self.x_start - self.padding, y_start))

        # Adjust button positions
        for i, button in enumerate(self.buttons):
            button.rect.x = self.x_start + self.padding * i * 2 + self.button_width * i
            button.rect.y = y_start + self.padding

        # check if button need to be disabled
        if self.display_compute or self.game_started:
            self.buttons[0].disabled = True
        else:
            self.buttons[0].disabled = False

        if self.enable_start and not self.game_started:
            self.buttons[1].disabled = False
        else:
            self.buttons[1].disabled = True

        if self.game_started:
            self.buttons[2].hidden = False
        else:
            self.buttons[2].hidden = True
        
        for button in self.buttons:
            button.draw(self.display_surface)

        # display computing text next to buttons
        if self.display_compute:
            text_surf = self.font.render('computing...', False, 'Black')
            self.display_surface.blit(text_surf, (
                self.x_start + self.padding * 4 + self.button_width * 2,
                y_start + self.padding * 2)
            )

    def draw_dropdowns(self):
        # background surface for dropdowns
        background_dropddown = pygame.Surface((self.background_width, self.dropdown_height + 2 * self.padding), pygame.SRCALPHA)
        background_dropddown.fill(self.backgroung_color)

        self.display_surface.blit(background_dropddown, (self.x_start - self.padding, self.y_start - self.padding))

        # dropdowns
        for dropdown in self.dropdowns:
            dropdown.draw(self.display_surface)
            dropdown.draw(self.display_surface)

    def toggle_assign(self):
        self.buttons[0].toggle()
    
    def toggle_start(self):
        self.buttons[1].toggle()

    def update(self):
        self.input()
        if self.display_menu:
            #self.draw_table()
            self.draw_buttons()
            self.draw_dropdowns()
