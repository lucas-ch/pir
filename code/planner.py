from player import *
from task import *
import random
from enum import Enum
import numpy as np
from scipy.optimize import linear_sum_assignment 

class AssignMethodsEnum(Enum):
    RANDOM = 1
    RANDOM_POSSIBLE = 2
    SSI = 3

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

                utility = players[i].bid(task)
                if utility > -8000:
                    self.assign_task(task, players[i])
                    task_assigned = True

    def assign_tasks_ssi(self, tasks:list[Task], players:list[Player]):
        for task in tasks:
            min_utility = 0
            winner:Player
            for player in players:
                utility = player.bid(task)
                if utility > min_utility:
                    min_utility = utility
                    winner = player
            
            if winner:
                self.assign_task(task, winner)

    def assign_tasks_st_sr_ia_greedy(self, tasks:list[Task], players:list[Player]):
        if len(tasks) > len(players):
            return "error"
        
        bids = np.zeros((len(tasks), len(players)))
        for i, task in enumerate(tasks):
            for j, player in enumerate(players):
                utility = player.bid(task)
                bids[i][j] = utility

        for _ in tasks:
            i, j = np.unravel_index(bids.argmax(), bids.shape)
            self.assign_task(tasks[i], players[j])
            bids[i,] = 0
            bids[:, j] = 0

    def assign_tasks_st_sr_ia_linear_optimization(self, tasks:list[Task], players:list[Player]):
            if len(tasks) > len(players):
                return "error"

            bids = np.zeros((len(tasks), len(players)))
            for i, task in enumerate(tasks):
                for j, player in enumerate(players):
                    utility = player.bid(task)
                    bids[i][j] = utility
            
            row_indices, col_indices = linear_sum_assignment(bids, maximize=True)
            for i in row_indices:
                self.assign_task(tasks[i], players[col_indices[i]])

    def assign_tasks_st_sr_ia_auction_algorithm(self, tasks:list[Task], players:list[Player]):
            if len(tasks) > len(players):
                return "error"

            # bids
            bids = np.zeros((len(tasks), len(players)))
            for i, task in enumerate(tasks):
                for j, player in enumerate(players):
                    utility = player.bid(task)
                    bids[i][j] = utility

            # assign randomly tasks to players, random price
            assignments = np.zeros((len(tasks), len(players)))
            prices = np.ones(len(tasks))*500
            for i, _ in enumerate(tasks):
                assignments[i][i]=1

            # reassign tasks
            while True:
                # check if someone is unhappy with the current assignement
                for j, player in enumerate(players):
                    everyone_happy = True
                    player_assignment = np.where(assignments[:,j] == 1)[0]
                    player_bids = bids[:,j]
                    player_profits_by_task = player_bids - prices
                    player_preferred_task = player_profits_by_task.argmax()

                    if player_profits_by_task[player_preferred_task] > player_profits_by_task[player_assignment] + 1:
                        everyone_happy = False
                        
                        # find other player
                        other_player = np.where(assignments[player_preferred_task,:] == 1)[0]

                        # swap task
                        assignments[player_assignment, other_player] = 1
                        assignments[player_preferred_task, other_player] = 0

                        assignments[player_preferred_task, j] = 1
                        assignments[player_assignment, j] = 0

                        # new price
                        player_profits_by_task.sort()
                        prices[player_preferred_task] = prices[player_preferred_task] + player_profits_by_task[-1] - player_profits_by_task[-2] + 1

                        #only one swap per turn
                        break
                
                # if no swap, no new turn
                if everyone_happy:
                    break

            # tasks assignement from result
            for i, task_assignment in enumerate(assignments):
                player_assigned = task_assignment.argmax()
                self.assign_task(tasks[i], players[player_assigned])

    def assign_tasks(self, tasks:list[Task], players:list[Player], method: str):
        if method == AssignMethodsEnum.RANDOM.name:
            self.assign_tasks_random(tasks, players)
        if method == AssignMethodsEnum.RANDOM_POSSIBLE.name:
            self.assign_tasks_random_possible(tasks, players)
        if method == AssignMethodsEnum.SSI.name:
            self.assign_tasks_ssi(tasks, players)
