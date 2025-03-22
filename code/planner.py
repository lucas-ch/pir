import json
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
            winner:Player = None
            for player in players:
                bid = player.bid(task)
                if bid > highest_bid:
                    highest_bid = bid
                    winner = player
            
            if winner is not None:
                self.assign_task(task, winner)
        
        return []

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
    
    def compute_planned_time(self, players:list[Player]):
        planned_time = 0
        for player in players:
            if player.planned_time > planned_time:
                planned_time = player.planned_time

        return planned_time

    def compute_total_distance(self, players:list[Player]):
        total_distance = 0
        for player in players:
            total_distance += len(sum(player.planned_path, []))

        return total_distance

    def assign_tasks_dias(self, tasks:list[Task], players:list[Player], nb_round:int, random: bool):

            self.assign_tasks_ssi(tasks, players)
            total_utility = self.compute_total_utility(players)
            total_distance = self.compute_total_distance(players)
            planned_time = self.compute_planned_time(players)

            result = AssignResult()
            result.ssi_init_distance = total_distance
            result.ssi_init_planned_time = planned_time
            result.ssi_init_utility = total_utility

            if random:
                self.assign_tasks_random_possible(tasks, players)
                total_utility = self.compute_total_utility(players)
                total_distance = self.compute_total_distance(players)
                planned_time = self.compute_planned_time(players)

                result.random_init_distance = total_distance
                result.random_init_planned_time= planned_time
                result.random_init_utility = total_utility

            total_distance_evolution = [total_distance]
            total_utility_evolution = [total_utility]
            planned_time_evolution = [planned_time]

            everyone_happy = 0
            round_number=0
            while everyone_happy == 0 and round_number < nb_round:
                round_number += 1
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

                            player.remove_task(task)
                            self.assign_task(task, winning_player)

                            total_utility = self.compute_total_utility(players)
                            total_utility_evolution.append(total_utility)

                            total_distance = self.compute_total_distance(players)
                            total_distance_evolution.append(total_distance)

                            planned_time = self.compute_planned_time(players)
                            planned_time_evolution.append(planned_time)

            result.planned_time_evolution = planned_time_evolution
            result.total_distance_evolution = total_distance_evolution
            result.total_utility_evolution = total_utility_evolution

            return result



    def assign_tasks(self, tasks:list[Task], players:list[Player], method: str, nb_round=10, random = False):
        for player in players:
            player.tasks = []

        if method == AssignMethodsEnum.RANDOM.name:
            return self.assign_tasks_random(tasks, players)
        if method == AssignMethodsEnum.RANDOM_POSSIBLE.name:
            return self.assign_tasks_random_possible(tasks, players)
        if method == AssignMethodsEnum.SSI.name:
            return self.assign_tasks_ssi(tasks, players)
        if method == AssignMethodsEnum.DIAS.name:
            return self.assign_tasks_dias(tasks, players, nb_round, random)

class AssignResult:
    def __init__(self):
        self.random_init_utility = 0
        self.random_init_distance = 0
        self.random_init_planned_time = 0
        self.ssi_init_utility = 0
        self.ssi_init_distance = 0
        self.ssi_init_planned_time= 0
        self.total_utility_evolution = 0
        self.total_distance_evolution = 0
        self.planned_time_evolution = 0

    def to_dict(self):
        return self.__dict__

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=4)
