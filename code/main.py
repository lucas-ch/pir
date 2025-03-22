import threading
from settings import *
from player import *
from player_info import *
from player_path import *
import pygame
from sprites import *
from item import *
from item_info import *
from planner import *
from task import *
from utils import *
from pytmx.util_pygame import load_pygame
from menu import Menu
import os

class Game:
    def __init__(self):
        # Setup
        pygame.init()

        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption('PIR')
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False

        # reset counters
        Player.reset_counter()
        Item.reset_counter()

        # Groups 
        self.all_sprites = pygame.sprite.Group()
        self.info = pygame.sprite.Group()
        self.players: pygame.sprite.Group[Player] = pygame.sprite.Group()
        self.players_path = pygame.sprite.Group()

        # Planner
        self.assignement_method = AssignMethodsEnum.RANDOM.name
        self.planner = Planner()
        self.assign_tasks_flag = False # in order to assign task only the frame after button is clicked

        # Menu
        self.menu = Menu(False, [], self.assignement_method)

        self.setup()

    def run(self):
        while self.running:
                
            # dt
            dt = self.clock.tick(60)

            if self.assign_tasks_flag:
                self.assign_tasks_flag = False
                self.menu.display_compute = True  # Affiche un indicateur de calcul en cours

                def assign_tasks_thread():
                    self.planner.assign_tasks(self.planner.tasks, list(self.players), self.assignement_method)
                    self.menu.display_compute = False  # Cache l'indicateur
                    self.menu.enable_start = True  # Active le bouton Start

                threading.Thread(target=assign_tasks_thread, daemon=True).start()


            # event loop 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:  # Appuyer sur 'P' pour basculer en pause
                        self.paused = not self.paused

            # Handle custom menu events
                if event.type == EventsEnum.TASK_ASSIGNED_CLICKED.value:
                    self.menu.display_compute = True
                    self.assign_tasks_flag = True

                if event.type == EventsEnum.START_CLICKED.value:
                    self.start_game()

                if event.type == EventsEnum.METHOD_CHANGED.value:
                    self.assignement_method = event.dict["value"]

                if event.type == EventsEnum.RETRY_CLICKED.value:
                    self.__init__()

            if not self.paused:
                # update in the game is not paused
                self.all_sprites.update(dt)

            # draw
            self.display_surface.fill('black')


            self.all_sprites.draw(self.display_surface)
            self.info.draw(self.display_surface)



            # Dessine les trajets des joueurs
            for player_path in self.players_path:
                player_path.update(self.display_surface)

            self.menu.update()
            pygame.display.update()

        pygame.quit()
    
    def setup(self):
        map = load_pygame(os.path.join('data', 'level5.tmx'))
        self.walkability_matrix = [[0 for _ in range(map.width)] for _ in range(map.height)]

        for x, y, image in map.get_layer_by_name('Grass').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
            self.walkability_matrix[y][x] = 1

        for x, y, image in map.get_layer_by_name('Water').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
            self.walkability_matrix[y][x] = 2

        for obj in map.get_layer_by_name('Items'):
            item = Item(obj.properties["type"], (obj.x, obj.y), obj.image, (self.all_sprites))
            ItemInfo(item, (self.all_sprites, self.info))
            task = Task(item, "cut", 100)
            self.planner.tasks.append(task)

        for obj in map.get_layer_by_name('Merchants'):
            player = PlayerWaterPhobic((obj.x, obj.y), obj.image, (self.all_sprites, self.players), self.walkability_matrix, False)
            PlayerInfo(player, self.all_sprites)
            PlayerPath(player, self.players_path)
        for obj in map.get_layer_by_name('Characters'):
            player = PlayerWaterResistant((obj.x, obj.y), obj.image, (self.all_sprites, self.players), self.walkability_matrix, False)
            PlayerInfo(player, self.all_sprites)
            PlayerPath(player, self.players_path)

        self.menu.toggle_menu()
        self.menu.tasks = self.planner.tasks

    def start_game(self):
        self.menu.game_started = True
        for player in self.players:
            player.game_started = True

if __name__ == '__main__':
    game = Game()
    game.run()
