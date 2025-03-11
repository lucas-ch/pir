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
    DIAS = 4

class Planner:
    def __init__(self):
        self.tasks = []

    def is_tasks_all_done(self):
        tasks_done = [e for e in self.tasks if e.status == TaskStatusEnum.DONE.name]

        if len(self.tasks) > 0 and len(self.tasks) == len(tasks_done):
            return True
        
        return False

    def assign_task(self, task: Task, player:Player):
        player.assign_task(task)
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
            highest_bid = 0
            winner:Player
            for player in players:
                bid = player.bid(task)
                print(f'task {task.item.id}  player {player.id} bid {bid}')
                if bid > highest_bid:
                    highest_bid = bid
                    winner = player
            
            if winner is not None:
                print(f'task {task.item.id}  goes to player {winner.id}')
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

    def compute_total_utility(self, players:list[Player]):
        total_utility = 0
        for player in players:
            total_utility += player.total_utility

        return total_utility

    def assign_tasks_dias(self, tasks:list[Task], players:list[Player]):
            self.assign_tasks_random(tasks, players)
            total_utility = self.compute_total_utility(players)
            total_utility_evolution = [total_utility]
            print(f'total_utility {total_utility} ')

            everyone_happy = 0
            round_number=0
            while everyone_happy == 0 and round_number < 10:
                round_number += 1
                print(f'round {round_number}')
                everyone_happy = 1
                for player in players:
                    for task in player.tasks:
                        revenue_task = player.compute_revenue_task(task)

                        winning_player = None
                        highest_bid = revenue_task

                        for other_player in players:
                            if other_player.id != player.id:
                                bid = other_player.bid(task)

                                if bid > highest_bid:
                                    winning_player = other_player
                                    highest_bid = bid
                    
                        if winning_player is not None:
                            everyone_happy = 0
                            print(f'player {winning_player.id} bid {highest_bid} and player {player.id} value is {revenue_task}')
                            print(f'utility of player {winning_player.id} was {winning_player.total_utility}')
                            print(f'utility of player {player.id} was {player.total_utility}')

                            player.remove_task(task)
                            self.assign_task(task, winning_player)
                            print(f'task {task.item.id} assigned to player {winning_player.id}')
                            print(f'utility of player {winning_player.id} is now {winning_player.total_utility}')
                            print(f'utility of player {player.id} is now {player.total_utility}')

                            total_utility = self.compute_total_utility(players)
                            print(f'total_utility {total_utility} ')
                            total_utility_evolution.append(total_utility)
            
            print(total_utility_evolution)


    def assign_tasks(self, tasks:list[Task], players:list[Player], method: str):
        for player in players:
            player.tasks = []

        if method == AssignMethodsEnum.RANDOM.name:
            self.assign_tasks_random(tasks, players)
        if method == AssignMethodsEnum.RANDOM_POSSIBLE.name:
            self.assign_tasks_random_possible(tasks, players)
        if method == AssignMethodsEnum.SSI.name:
            self.assign_tasks_ssi(tasks, players)
        if method == AssignMethodsEnum.DIAS.name:
            self.assign_tasks_dias(tasks, players)
