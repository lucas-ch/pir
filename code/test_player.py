import unittest
from player import *
from settings import *

from pygame import *

class TestPlayer(unittest.TestCase):
    def test_compute_shortest_path(self):
        surf_tree = pygame.image.load('graphics/objects/tree_medium.png')

        item1 = Item("tree", (TILE_SIZE*10.0, 0.0), surf_tree, [])
        item2 = Item("tree", (TILE_SIZE*15.0, 0.0), surf_tree, [])
        task1 = Task(item1, "cut", 1000)
        task2 = Task(item2, "cut", 1000)
        tasks = [task1, task2]
        
        walkability_matrix = [[1 for _ in range(TILE_SIZE*50)] for _ in range(TILE_SIZE*50)]
        surf_player = pygame.image.load('graphics/character/down/0.png')
        player = Player((0.0, 0.0), surf_player, [], walkability_matrix, False)

        path = player.compute_shortest_path(tasks)
        self.assertEqual(len(path), 2)
        self.assertEqual(len(path[0]), 11)
        self.assertEqual(len(path[1]), 6)

    def compute_revenue_task(self):
        surf_tree = pygame.image.load('graphics/objects/tree_medium.png')

        item1 = Item("tree", (TILE_SIZE*10.0, 0.0), surf_tree, [])
        item2 = Item("tree", (TILE_SIZE*15.0, 0.0), surf_tree, [])
        task1 = Task(item1, "cut", 100)
        task2 = Task(item2, "cut", 100)
        tasks = [task1, task2]
        
        walkability_matrix = [[1 for _ in range(TILE_SIZE*50)] for _ in range(TILE_SIZE*50)]
        surf_player = pygame.image.load('graphics/character/down/0.png')
        player = Player((0.0, 0.0), surf_player, [], walkability_matrix, False)

        player.tasks = tasks
        revenue_task1 = player.compute_revenue_task(task1)
        revenue_task2 = player.compute_revenue_task(task2)
        self.assertEqual(revenue_task2, 90)
        self.assertEqual(revenue_task1, 95)

if __name__ == "__main__":
    unittest.main()
