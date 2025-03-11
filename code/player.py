from settings import *
from utils import *
from task import *
import pygame
from pathfinding.core.grid import Grid, GridNode
from pathfinding.finder.a_star import AStarFinder
import numpy as np

class Player(pygame.sprite.Sprite):
    _id_counter = 0
    _colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)]
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
        self.reward_factor = 0.95

        # graphics
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)
        self.color = Player._colors[self.id]

        # game initialisation
        self.game_started: bool = game_started
        self.walkability_matrix = walkability_matrix
        self.grid = Grid(matrix=self.walkability_matrix)

        self.tasks: list[Task] = []
        self.current_task: Task = None
        self.current_path: list = []

        #statistics
        self.planned_path: list = []
        self.total_utility = 0

        self.task_timer = 0  # Timer for health reduction

    @classmethod
    def reset_counter(cls):
        Player._id_counter = 0

    def assign_task(self, task: Task):
        task.item.color = self.color
        self.tasks.append(task)
        self.planned_path = self.compute_shortest_path(self.tasks.copy())
        self.total_utility = self.compute_total_utility()

    def remove_task(self, task:Task):
        self.tasks.remove(task)
        task.item.color = (255, 255, 255)
        self.planned_path = self.compute_shortest_path(self.tasks.copy())
        self.total_utility = self.compute_total_utility()

    # utility functions
    def compute_total_utility(self):
        total_distance = len(sum(self.planned_path, []))

        total_reward = 0
        total_action_cost = 0
        for i, task in enumerate(self.tasks):
            total_reward += (task.reward)*(self.reward_factor ** i)
            total_action_cost += self.compute_cost_action(task)

        return total_reward - total_action_cost - total_distance

    def compute_cost(self, action:float, distance:float):
        return action + distance

    def bid(self, task: Task):
        action = self.compute_cost_action(task)
        distance = self.compute_cost_distance(task)
        total_cost = self.compute_cost(action, distance)

        reward = task.reward * (self.reward_factor ** (len(self.tasks)))

        utility = reward - total_cost

        if utility > 0:
            return utility
        else:
            return -8000

    def compute_revenue_task(self, task: Task):
        if task not in self.tasks:
            return 0

        list_tasks = self.tasks.copy()
        list_tasks_without = list_tasks.copy()
        list_tasks_without.remove(task)

        shortest_path = self.compute_shortest_path(list_tasks)
        shortest_path_without = self.compute_shortest_path(list_tasks_without)

        distance_task = len(sum(shortest_path, [])) - len(sum(shortest_path_without, [])) - 1

        reward = task.reward * ( self.reward_factor ** (len(self.tasks) - 1))
        revenue_task = reward - distance_task - self.compute_cost_action(task)

        return revenue_task
    
    def compute_cost_distance(self, task: Task):
        if task in self.tasks:
            return 0

        shortest_path = self.compute_shortest_path(self.tasks.copy())

        task_list_with_new_task = self.tasks.copy()
        task_list_with_new_task.append(task)
        shortest_path_with_new_task = self.compute_shortest_path(task_list_with_new_task)

        distance_task = len(sum(shortest_path_with_new_task, [])) - len(sum(shortest_path, [])) - 1

        return distance_task

    def find_closest_task(self, character_pos, tasks: list[Task]):
        closest_task = tasks[0]
        shortest_distance = 8000

        for task in tasks:
            task_pos = (task.item.rect.x, task.item.rect.y)
                
            task_distance = len(self.find_path(character_pos, task_pos))
            if task_distance < shortest_distance:
                shortest_distance = task_distance
                closest_task = task
        
        return closest_task
    
    def compute_shortest_path(self, tasks: list[Task]):
        character_pos = (self.rect.x, self.rect.y)
        total_path = []

        while len(tasks) > 0:
            closest_task = self.find_closest_task(character_pos, tasks)
            closest_task_pos = (closest_task.item.rect.x, closest_task.item.rect.y)
            path = self.find_path(character_pos, closest_task_pos)
            total_path.append(path)

            tasks.remove(closest_task)
            character_pos = closest_task_pos

        return total_path

    def compute_cost_action(self, task: Task):
        item_type = task.item.type
        return 100/self.damage_per_blow[item_type]

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

    def start_next_task(self):
        todo_tasks = [e for e in self.tasks if e.status == TaskStatusEnum.TODO.name]


        if len(todo_tasks) > 0 and self.game_started:
            character_pos = (self.rect.x, self.rect.y)
            shortest_distance = 1000

            for task in todo_tasks:
                task_pos = (task.item.rect.x, task.item.rect.y)
                
                task_distance = len(self.find_path(character_pos, task_pos))
                if task_distance < shortest_distance:
                    shortest_distance = task_distance
                    next_task = task

            next_task.cost = self.compute_cost(self.compute_cost_action(task), - shortest_distance)
            self.start_task(next_task)

    # movements functions
    def find_path(self, a: tuple, b: tuple):
        start = self.grid.node(int(a[0] / TILE_SIZE), int(a[1] / TILE_SIZE))
        end = self.grid.node(int(b[0] / TILE_SIZE), int(b[1] / TILE_SIZE))

        finder = AStarFinder()
        path, _ = finder.find_path(start, end, self.grid)

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
        if self.current_task is None and self.game_started:
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