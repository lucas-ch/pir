from player import *
from task import *
import random
from enum import Enum

class AssignMethodsEnum(Enum):
    RANDOM = 1
    RANDOM_POSSIBLE = 2

class Planner:
    def __init__(self):
        self.tasks = []

    def is_tasks_all_done(self):
        tasks_done = [e for e in self.tasks if e.status == TaskStatusEnum.DONE.name]

        if len(self.tasks) > 0 and len(self.tasks) == len(tasks_done):
            return True
        
        return False

    def assign_task(self, task: Task, player:Player):
        player.tasks.append(task)
        task.assigned_to = player.id

    def assign_tasks_random(self, tasks:list[Task], players:list[Player]):
        for player in players:
            player.tasks = []

        nb_players = len(players)
        nb_tasks = len(tasks)

        if nb_players == 0 or nb_tasks == 0:
            return
        
        for task in tasks:
            task_assigned = False

            count = 0
            while task_assigned == False and count < 100:
                count += 1
                i = random.randint(0, nb_players - 1)
                self.assign_task(task, players[i])
                task_assigned = True

    def assign_tasks_random_possible(self, tasks:list[Task], players:list[Player]):
        for player in players:
            player.tasks = []

        nb_players = len(players)
        nb_tasks = len(tasks)

        if nb_players == 0 or nb_tasks == 0:
            return
        
        for task in tasks:
            task_assigned = False

            count = 0
            while task_assigned == False and count < 100:
                count += 1
                i = random.randint(0, nb_players - 1)

                utility = players[i].compute_utility(task)
                if utility > -8000:
                    self.assign_task(task, players[i])
                    task_assigned = True

    def assign_tasks(self, tasks:list[Task], players:list[Player], method: str):
        if method == AssignMethodsEnum.RANDOM.name:
            self.assign_tasks_random(tasks, players)
        if method == AssignMethodsEnum.RANDOM_POSSIBLE.name:
            self.assign_tasks_random_possible(tasks, players)
