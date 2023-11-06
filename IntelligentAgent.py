# Samuel Braun slb2250
import random
import math
from BaseAI import BaseAI
import time

class IntelligentAgent(BaseAI):

    # allows for get_full_heuristic to access previous move
    def __init__(self):
        self.curr_move = 0
    
    # returns the best move
    def getMove(self, grid):
        alpha = float('-inf')
        beta = float('inf')
        best_move, _ = self.expectiminimax(grid, 0, True, alpha, beta, time.process_time())
        if not grid.getAvailableMoves():
            return None
        return best_move

    # expectiminimax algorithm
    def expectiminimax(self, grid, depth, max_player, alpha, beta, start_time, move=None, curr_move=None):
        if depth > 4 or time.process_time() - start_time > 0.19:
            return None, self.get_full_heuristic(grid, move, curr_move)
        
        # max player
        best_move = None
        if max_player:
            util = float('-inf')
            if not grid.getAvailableMoves():
                return grid, self.get_full_heuristic(grid, move, self.curr_move)
            
            for move, new_grid in grid.getAvailableMoves():
                _, eval = self.expectiminimax(new_grid, depth+1, False, alpha, beta, start_time, move, self.curr_move)
                
                if eval > util:
                    util = eval
                    best_move = move
               
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # alpha beta pruning

            self.curr_move = best_move
            return best_move, util

        # min player
        else:
            grid_child, returned_util = None, float('inf') # initial beta
            
            available_cells = grid.getAvailableCells()
            for cell in available_cells:
                grid_2, grid_4, min_util = grid.clone(), grid.clone(), 0
                grid_2.setCellValue(cell, 2)
                grid_4.setCellValue(cell, 4)
                _, eval_2 = self.expectiminimax(grid_2, depth+1, True, alpha, beta, start_time)
                _, eval_4 = self.expectiminimax(grid_4, depth+1, True, alpha, beta, start_time)

                min_util = 0.9 * eval_2 + 0.1 * eval_4

                if min_util < returned_util:
                    returned_util = min_util
                    grid_child = grid
                if returned_util <= alpha:
                    break
                if returned_util < beta:
                    beta = returned_util

            return grid_child, returned_util
       
    # calculates weights for heuristic based on state of grid
    def get_weights(self, grid):
        max_tile = grid.getMaxTile()
        empty_cells = len(grid.getAvailableCells())

        weights = {
            'empty': 4.0, #4.0
            'monotonicity': 2.2,   #2.2
            'smoothness': 1.0,  #1.0
            'random': 0.5,
            'merges': 1.0, #1.0
            'open_2_or_4': 2.0,
            'corner': 1.0,
            'maxy': 3.5 #3.5
        }

        if max_tile == 1024:
            weights['empty'] += 1.0
        elif empty_cells <= 2:
            weights['empty'] += 2.0
            weights['merges'] += 1.0


        return weights, max_tile
    
    # calculates full heuristic based on weights and state of grid
    def get_full_heuristic(self, grid, move, prev_move):
        weights, max_tile = self.get_weights(grid)
        
        empty_score = self.h_empty(grid)
        monotonicity_score = self.h_monotinicity(grid)
        smoothness_score = self.h_smoothness(grid)
        random_score = self.h_random(grid)
        merges = self.h_large_merges(grid)
        in_corner = self.h_top_corner(grid)
        
        heuristic = (
            weights['empty'] * empty_score +
            weights['monotonicity'] * monotonicity_score +
            weights['smoothness'] * smoothness_score +
            weights['random'] * random_score +
            weights['merges'] * merges +
            weights['maxy'] + max_tile
        )

        if in_corner:
            heuristic = heuristic * 30
        if move == 1:
            heuristic = heuristic / 10000
        if prev_move == 1 and move == 0:
            heuristic = heuristic * 100000000

        return heuristic
    
    # compares values of top-left and top-right corners and returns larger value
    def h_compare_top_corners(self, grid):
        left = grid.map[0][0]
        right = grid.map[0][grid.size - 1]
        
        if left > right:
            larger_corner = 2
            diff = left - right
        else:
            larger_corner = 3
            diff = right - left
            
        return larger_corner, diff

    # heuristic evaluates how many empty cells are on the grid
    def h_empty(self, grid):
        empty_cells = len(grid.getAvailableCells())
        return empty_cells
    
    # heuristic evaluates monotonicity of tiles in rows and columns
    def h_monotinicity(self, grid):
        monotonicity = 0
        for i in range(grid.size):
            m = 0 
            for j in range(grid.size - 1):
                if grid.map[i][j] >= grid.map[i][j + 1]:
                    m += 1
            monotonicity += m  # normalize --> unit vectorish
        
        return monotonicity / ((grid.size - 1) * grid.size)
    
    # heuristic evaluates smoothness of transitions between tiles
    def h_smoothness(self, grid):
        smoothness = 0
        for i in range(grid.size):
            for j in range(grid.size):
                if grid.map[i][j] != 0:
                    
                    for direction in [(0, 1), (1, 0)]:
                        x, y = i + direction[0], j + direction[1]
                        if x < grid.size and y < grid.size and grid.map[x][y] != 0:
                            smoothness -= abs(math.log2(grid.map[i][j]) - math.log2(grid.map[x][y]))
        return smoothness
    
    # for heuristic: generates random value to add variability to heuristic function
    def h_random(self, grid):
        return random.random()
    
    # heuristic evaluates how many large merges are possible
    def h_large_merges(self, grid):
        merge_count = 0
        for i in range(grid.size):
            for j in range(grid.size):
                tile = grid.map[i][j]

                if tile > 0:
                    # Check the tile to the right and below, to avoid counting duplicates
                    for dx, dy in [(0, 1), (1, 0)]:
                        new_i, new_j = i + dx, j + dy
                        if 0 <= new_i < grid.size and 0 <= new_j < grid.size:
                            if grid.map[new_i][new_j] == tile:
                                merge_count += 1

        return merge_count
    
    # heuristic evaluates if top left or top right corner is the largest tile
    def h_top_corner(self, grid):
        max_tile = grid.getMaxTile()
        top_left = grid.map[0][0]
        top_right = grid.map[0][grid.size - 1]
        
        if top_left == max_tile or top_right == max_tile:
            return True
        else:
            return False
