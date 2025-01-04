from settings import *
from utils import *
from task import *
import pygame
from pathfinding.core.grid import Grid, GridNode
from pathfinding.finder.a_star import AStarFinder

class Player(pygame.sprite.Sprite):
    _id_counter = 0

    def __init__(self,
                 pos: tuple[int],
                 surf:pygame.Surface,
                 groups:list[pygame.sprite.Group],
                 walkability_matrix:list[list[int]],
                 game_started:bool):
        super().__init__(groups)

        # id
        self.id = Player._id_counter
        Player._id_counter += 1

        # properties
        self.speed = 10
        self.damage_per_blow = {
            "mushroom": 50,
            "tree": 20
        }
        self.blow_per_second = 3

        # graphics
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)

        # game initialisation
        self.game_started: bool = game_started
        self.walkability_matrix = walkability_matrix
        self.tasks: list[Task] = []
        self.current_task: Task = None
        self.current_path: list = []

        self.task_timer = 0  # Timer for health reduction

    @classmethod
    def reset_counter(cls):
        Player._id_counter = 0

    # utility functions
    def compute_utility(self, task: Task):
        return self.compute_utility_action(task) + self.compute_utility_distance(task)
    
    def compute_utility_distance(self, task: Task):
        character_pos = (self.rect.x, self.rect.y)
        task_pos = (task.item.rect.x, task.item.rect.y)

        path = self.find_path(character_pos, task_pos)

        if path is not None and len(path) > 0:
            return -len(path)
        else:
            return -8000

    def compute_utility_action(self, task: Task):
        item_type = task.item.type
        return - self.damage_per_blow[item_type]

    # tasks functions
    def start_task(self, task: Task):
        self.current_task = task
        task.setStatus(TaskStatusEnum.DOING.name)
        character_pos = (self.rect.x, self.rect.y)
        task_pos = (task.item.rect.x, task.item.rect.y)
        self.current_path = self.find_path(character_pos, task_pos)

    def perform_task(self, dt:int):
        if self.current_task is None:
            return

        item = self.current_task.item

        character_pos = convert_coordinates_to_tile(self.rect)
        task_pos = convert_coordinates_to_tile(item.rect)

        if character_pos == task_pos:
            self.task_timer += dt
            if self.task_timer >= 1000/self.blow_per_second:
                item.decrease_health(self.damage_per_blow[item.type])
                self.task_timer = 0

                if not item.alive():
                    self.complete_task()

    def complete_task(self):
        self.current_task.setStatus(TaskStatusEnum.DONE.name)
        self.current_task = None
        self.tasks.pop(0)

    def start_next_task(self):
        if len(self.tasks) > 0 and self.game_started:
            next_task = self.tasks[0]
            next_task.utility = self.compute_utility(next_task)

            self.start_task(next_task)

    # movements functions
    def find_path(self, a: tuple, b: tuple):
        grid = Grid(matrix=self.walkability_matrix)
        start = grid.node(int(a[0] / TILE_SIZE), int(a[1] / TILE_SIZE))
        end = grid.node(int(b[0] / TILE_SIZE), int(b[1] / TILE_SIZE))

        finder = AStarFinder()
        path, _ = finder.find_path(start, end, grid)

        return path

    def move(self):
        if self.current_path is None or len(self.current_path) == 0:
            return
        if (
            self.current_path[0].x * TILE_SIZE == self.rect.x
            and self.current_path[0].y * TILE_SIZE == self.rect.y
        ):
            self.current_path.pop(0)
        else:
            self.move_to_tile(self.current_path[0])

    def move_to_tile(self, tile: GridNode):
        x, y = self.rect.x, self.rect.y

        if (tile.x) * TILE_SIZE - self.rect.x > 0:
            x = min(self.rect.x + self.speed, tile.x * TILE_SIZE)

        if (tile.x) * TILE_SIZE - self.rect.x < 0:
            x = max(self.rect.x - self.speed, tile.x * TILE_SIZE)

        if (tile.y) * TILE_SIZE - self.rect.y > 0:
            y = min(self.rect.y + self.speed, tile.y * TILE_SIZE)

        if (tile.y) * TILE_SIZE - self.rect.y < 0:
            y = max(self.rect.y - self.speed, tile.y * TILE_SIZE)

        self.rect = self.image.get_frect(topleft=(x, y))

    # loop update function
    def update(self, dt:int):
        if self.current_task is None:
            self.start_next_task()
        self.move()
        self.perform_task(dt)

# specific players class 
class PlayerWaterResistant(Player):
    def __init__(self, pos, surf, groups, walkability_matrix, game_started):
        super().__init__(pos, surf, groups, walkability_matrix, game_started)
        self.speed = 10

class PlayerWaterPhobic(Player):
    def __init__(self, pos, surf, groups, walkability_matrix, game_started):
        walkability_matrix = [[0 if value == 2 else value for value in row] for row in walkability_matrix]
        super().__init__(pos, surf, groups, walkability_matrix, game_started)
        self.speed = 20