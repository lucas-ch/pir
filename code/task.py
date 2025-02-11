from item import *
from enum import Enum

class TaskStatusEnum(Enum):
    TODO = 1
    DOING = 2
    DONE = 3

class Task:
    def __init__(self, item:Item, type:str, reward: int):
        self.status = TaskStatusEnum.TODO.name
        self.item = item
        self.type = type
        self.assigned_to = None
        self.reward = reward
        self.cost = 0
    
    def setStatus(self, status:str):
        self.status = status
