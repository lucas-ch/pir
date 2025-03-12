import json
import threading
import time
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

class GameResult:
    def __init__(self, id, reward_factor, nb_round, assignement_method, random_init):
        self.id = id
        self.assignement_method = assignement_method
        self.nb_round_max = nb_round
        self.resolution_time: 0
        self.communication_number = 0
        self.total_utility = 0
        self.total_distance = 0
        self.nb_tasks_done = 0
        self.tasks_stats = (0, 0)
        self.reward_factor = reward_factor
        self.random_init = random_init
        self.evolution = []

    def compute_assignment_result(self, players: list[Player], tasks: list[Task]):
        self.communication_number = self.compute_communication_number(players)
        self.total_utility = self.compute_total_utility(players)
        self.total_distance = self.compute_total_distance(players)
        self.nb_tasks_done = self.compute_tasks_done(tasks)
        self.tasks_stats = self.compute_tasks_stats(players)

    def compute_tasks_done(self, tasks: list[Task]):
        tasks_done = 0
        for task in tasks:
            if task.assigned_to is not None:
                tasks_done +=1
        return tasks_done
                
    def compute_tasks_stats(self, players: list[Player]):
        max_task = 0
        min_task = 100
        for player in players:
            if len(player.tasks) > max_task:
                max_task = len(player.tasks)
            if len(player.tasks) < min_task:
                min_task = len(player.tasks)
        return (min_task, max_task)

    def compute_total_utility(self, players: list[Player]):
        total_utility = 0
        for player in players:
            total_utility += player.total_utility

        return total_utility
    
    def compute_communication_number(self, players: list[Player]):
        communication_number = 0
        for player in players:
            communication_number += player.communication_number

        return communication_number

    def compute_total_distance(self, players: list[Player]):
        distance = 0
        for player in players:
            distance += len(sum(player.planned_path, []))

        return distance

    def __repr__(self):
        return json.dumps(self.__dict__, indent=4)

    def save_to_file(self, filename):
        with open(filename, "a") as file:
            json.dump(self.__dict__, file, indent=4)
            file.write("\n")

    def to_dict(self):
        return self.__dict__

class Game:
    init_count = 0
    game_results = []

    def __init__(self):
        # Setup
        pygame.init()

        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption('PIR')
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.randomize_position = True

        # reset counters
        Player.reset_counter()
        Item.reset_counter()

        # Groups 
        self.all_sprites = pygame.sprite.Group()
        self.players: pygame.sprite.Group[Player] = pygame.sprite.Group()
        self.players_path = pygame.sprite.Group()

        # Planner
        if Game.init_count > 350:
            pygame.quit()

        if Game.init_count < 300:
            self.assignement_method = AssignMethodsEnum.DIAS.name
            self.reward_factor = 1
            self.random_init = True

        if Game.init_count < 250:
            self.assignement_method = AssignMethodsEnum.DIAS.name
            self.reward_factor = 0.95
            self.random_init = True

        if Game.init_count < 200:
            self.assignement_method = AssignMethodsEnum.DIAS.name
            self.reward_factor = 1
            self.random_init = False

        if Game.init_count < 150:
            self.assignement_method = AssignMethodsEnum.DIAS.name
            self.reward_factor = 0.95
            self.random_init = False

        if Game.init_count < 100:
            self.assignement_method = AssignMethodsEnum.SSI.name
            self.reward_factor = 1
            self.random_init = True

        if Game.init_count < 50:
            self.assignement_method = AssignMethodsEnum.SSI.name
            self.reward_factor = 0.95
            self.random_init = True

        self.nb_round = 10 #for dias

        self.game_result = GameResult(Game.init_count, self.reward_factor, self.nb_round, self.assignement_method, self.random_init)


        self.planner = Planner()
        self.assign_tasks_flag = False # in order to assign task only the frame after button is clicked

        # Menu
        self.menu = Menu(False, [], self.assignement_method)

        #stats
        self.start_time = 0
        self.end_time = 0

        self.setup()

    def run(self):
        
        while self.running:
                
            # dt
            dt = self.clock.tick(60)

            if self.planner.is_tasks_all_done() and self.randomize_position:
                self.end_time = time.time()  # Fin du chronomètre
                elapsed_time = self.end_time - self.start_time
                self.game_result.resolution_time = elapsed_time

                print(self.game_result)
                Game.game_results.append(self.game_result.to_dict())
                Game.init_count += 1

                # Sauvegarde après chaque ajout
                with open('result.txt', "w") as file:
                    json.dump(Game.game_results, file, indent=4)

                self.__init__()

            if self.assign_tasks_flag:
                self.assign_tasks_flag = False
                self.menu.display_compute = True  # Affiche un indicateur de calcul en cours

                def assign_tasks_thread():
                    self.game_result.evolution = self.planner.assign_tasks(self.planner.tasks, list(self.players), self.assignement_method, self.nb_round, self.random_init)
                    self.menu.display_compute = False  # Cache l'indicateur
                    self.menu.enable_start = True  # Active le bouton Start

                    if self.randomize_position:
                        self.menu.game_started = True
                        self.start_game()
                        self.start_time = time.time()  # Démarrage du chronomètre
                    
                    self.game_result.compute_assignment_result(self.players, self.planner.tasks)

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

            # Dessine les trajets des joueurs
            for player_path in self.players_path:
                player_path.update(self.display_surface)

            self.menu.update()
            pygame.display.update()

        pygame.quit()
    
    def setup(self):
        map = load_pygame(os.path.join('data', 'level_final.tmx'))
        self.walkability_matrix = [[0 for _ in range(map.width)] for _ in range(map.height)]

        for x, y, image in map.get_layer_by_name('Grass').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
            self.walkability_matrix[y][x] = 1

        for x, y, image in map.get_layer_by_name('Water').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
            self.walkability_matrix[y][x] = 2

        for obj in map.get_layer_by_name('Items'):
            if self.randomize_position:
                x = random.randint(0, int((TILE_SIZE * 99 )) )
                y = random.randint(0, int((TILE_SIZE * 99)) )
            else:
                x = obj.x
                y = obj.y

            item = Item(obj.properties["type"], (x, y), obj.image, (self.all_sprites))
            ItemInfo(item, self.all_sprites)
            task = Task(item, "cut", 150)
            self.planner.tasks.append(task)

        for obj in map.get_layer_by_name('Merchants'):
            if self.randomize_position:
                x = random.randint(0, int((TILE_SIZE * 99 )) )
                y = random.randint(0, int((TILE_SIZE * 99)) )
            else:
                x = obj.x
                y = obj.y

            player = PlayerWaterPhobic((x, y), obj.image, (self.all_sprites, self.players), self.walkability_matrix, False, self.reward_factor)
            PlayerInfo(player, self.all_sprites)
            PlayerPath(player, self.players_path)
        for obj in map.get_layer_by_name('Characters'):
            if self.randomize_position:
                x = random.randint(0, int((TILE_SIZE * 44 )) )
                y = random.randint(0, int((TILE_SIZE * 34)) )
            else:
                x = obj.x
                y = obj.y
            player = PlayerWaterResistant((x, y), obj.image, (self.all_sprites, self.players), self.walkability_matrix, False, self.reward_factor)
            PlayerInfo(player, self.all_sprites)
            PlayerPath(player, self.players_path)

        self.menu.toggle_menu()
        self.menu.tasks = self.planner.tasks

        if self.randomize_position:
            self.assign_tasks_flag = True


    def start_game(self):
        self.menu.game_started = True
        for player in self.players:
            player.game_started = True

if __name__ == '__main__':
    game = Game()
    game.run()
