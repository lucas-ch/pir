import unittest
from planner import *
from pygame import *

class TestGreedy(unittest.TestCase):
    def test_assign_task_st_sr_ia_greedy(self):
        planner = Planner()

        surf_tree = pygame.image.load('graphics/objects/tree_medium.png')

        item1 = Item("tree", (1179.0, 921.0), surf_tree, [])
        item2 = Item("tree", (174.0, 182.0), surf_tree, [])
        task1 = Task(item1, "cut", 1000)
        task2 = Task(item2, "cut", 1000)
        tasks = [task1, task2]
        
        walkability_matrix = [[1 for _ in range(500)] for _ in range(500)]
        surf_player = pygame.image.load('graphics/character/down/0.png')
        player1 = Player((1127.0, 479.0), surf_player, [], walkability_matrix, False)
        player2 = Player((50.0, 50.0), surf_player, [], walkability_matrix, False)
        players = [player1, player2]

        planner.assign_tasks_st_sr_ia_greedy(tasks, players)

        self.assertEqual(len(player2.tasks), 1)
        self.assertEqual(len(player1.tasks), 1)
        self.assertEqual(player1.tasks[0],task1)
        self.assertEqual(player2.tasks[0], task2)

    def test_assign_tasks_st_sr_ia_linear_optimization(self):
        planner = Planner()

        surf_tree = pygame.image.load('graphics/objects/tree_medium.png')

        item1 = Item("tree", (1179.0, 921.0), surf_tree, [])
        item2 = Item("tree", (538.0, 484.0), surf_tree, [])
        item3 = Item("tree", (174.0, 182.0), surf_tree, [])

        task1 = Task(item1, "cut", 1000)
        task2 = Task(item2, "cut", 1000)
        task3 = Task(item3, "cut", 1000)

        tasks = [task1, task2, task3]
        
        walkability_matrix = [[1 for _ in range(500)] for _ in range(500)]
        surf_player = pygame.image.load('graphics/character/down/0.png')
        player1 = Player((1127.0, 479.0), surf_player, [], walkability_matrix, False)
        player2 = Player((50.0, 50.0), surf_player, [], walkability_matrix, False)
        player3 = Player((500.0, 500.0), surf_player, [], walkability_matrix, False)

        players = [player1, player2, player3]

        planner.assign_tasks_st_sr_ia_linear_optimization(tasks, players)

        self.assertEqual(len(player2.tasks), 1)
        self.assertEqual(len(player1.tasks), 1)
        self.assertEqual(len(player3.tasks), 1)

        self.assertEqual(player1.tasks[0],task1)
        self.assertEqual(player2.tasks[0], task3)
        self.assertEqual(player3.tasks[0], task2)

    def test_assign_tasks_st_sr_ia_auction_algorithm(self):
        planner = Planner()

        surf_tree = pygame.image.load('graphics/objects/tree_medium.png')

        item1 = Item("tree", (1179.0, 921.0), surf_tree, [])
        item2 = Item("tree", (538.0, 484.0), surf_tree, [])
        item3 = Item("tree", (174.0, 182.0), surf_tree, [])

        task1 = Task(item1, "cut", 1000)
        task2 = Task(item2, "cut", 1000)
        task3 = Task(item3, "cut", 1000)

        tasks = [task1, task2, task3]
        
        walkability_matrix = [[1 for _ in range(500)] for _ in range(500)]
        surf_player = pygame.image.load('graphics/character/down/0.png')
        player1 = Player((1127.0, 479.0), surf_player, [], walkability_matrix, False)
        player2 = Player((50.0, 50.0), surf_player, [], walkability_matrix, False)
        player3 = Player((500.0, 500.0), surf_player, [], walkability_matrix, False)

        players = [player1, player2, player3]

        planner.assign_tasks_st_sr_ia_auction_algorithm(tasks, players)

        self.assertEqual(len(player2.tasks), 1)
        self.assertEqual(len(player1.tasks), 1)
        self.assertEqual(len(player3.tasks), 1)

        self.assertEqual(player1.tasks[0],task1)
        self.assertEqual(player2.tasks[0], task3)
        self.assertEqual(player3.tasks[0], task2)

if __name__ == "__main__":
    unittest.main()
