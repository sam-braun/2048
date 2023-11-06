# Samuel Braun slb2250
import random
import math
from BaseAI import BaseAI
import time

class IntelligentAgent(BaseAI):

    def __init__(self):
        self.curr_move = 0
        
    def getMove(self, grid):
        alpha = float('-inf')
        beta = float('inf')
        best_move, _ = self.expectiminimax(grid, 0, True, alpha, beta, time.process_time())
        if not grid.getAvailableMoves():
            return None
        return best_move

    def expectiminimax(self, grid, depth, max_player, alpha, beta, start_time, move=None, curr_move=None):
        if depth > 4 or time.process_time() - start_time > 0.2:
            return None, self.h4(grid, move, curr_move)
        
        best_move = None
        if max_player:
            util = float('-inf')
            if not grid.getAvailableMoves():
                return grid, self.h4(grid, move, self.curr_move)
            
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


    def h0(self, grid):
        return grid.getMaxTile()
       
    def calculate_weights(self, grid):
        max_tile = grid.getMaxTile()
        empty_cells = len(grid.getAvailableCells())

        weights = {
            'empty': 4.0, #4.0
            'monotonicity': 2.2,   #2.2
            'smoothness': 1.0,  #1.0
            'random': 0.5,
            # 'uniformity': 0.0,
            # 'greedy': 0.0,
            'merges': 1.0, #1.0
            # 'non_monotonic_penalty': 0.0,
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
    
    def h4(self, grid, move, prev_move):
        weights, max_tile = self.calculate_weights(grid)
        
        empty_score = self.h_empty(grid)
        monotonicity_score = self.h_monotinicity(grid)
        smoothness_score = self.h_smoothness(grid)
        random_score = self.h_random(grid)
        # uniformity_score = self.h_uniformity(grid)
        # greedy_score = self.h_greedy(grid)
        merges = self.h_large_merges(grid)
        # non_mono_penalty_score = self.h_non_monotonic_penalty(grid)
        open_2_or_4_score = self.h_open_spot_next_to_2_or_4(grid)
        in_corner = self.h_top_corner(grid)

        
        h4 = (

            weights['empty'] * empty_score +
            weights['monotonicity'] * monotonicity_score +
            weights['smoothness'] * smoothness_score +
            weights['random'] * random_score +
            # weights['uniformity'] * uniformity_score +
            # weights['greedy'] * greedy_score +
            weights['merges'] * merges +
            # weights['non_monotonic_penalty'] * non_mono_penalty_score +
            weights['open_2_or_4'] * open_2_or_4_score +
            max_tile * weights['maxy']
        )

        if in_corner:
            h4 = h4 * 30
        if move == 1:
            h4 = h4 / 10000
        if prev_move == 1 and move == 0:
            h4 = h4 * 100000000

        return h4
    
    def compare_top_corners(self, grid):
        left = grid.map[0][0]
        right = grid.map[0][grid.size - 1]
        
        if left > right:
            larger_corner_position = 2
            difference = left - right
        else:
            larger_corner_position = 3
            difference = right - left
            
        return larger_corner_position, difference


    def h_empty(self, grid):
        empty_cells = len(grid.getAvailableCells())
        return empty_cells
    
    def h_monotinicity(self, grid):
        monotonicity = 0
        for i in range(grid.size):
            m = 0 
            for j in range(grid.size - 1):
                if grid.map[i][j] >= grid.map[i][j + 1]:
                    m += 1
            monotonicity += m / (grid.size - 1)  # normalized to [0,1]
        
        return monotonicity
    
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
    
    def h_random(self, grid):
        return random.random()
    
    # def h_uniformity(self, grid):
    #     uniformity = 0
    #     for i in range(grid.size):
    #         for j in range(grid.size):
    #             if grid.map[i][j] != 0:
    #                 for direction in [(0, 1), (1, 0)]:
    #                     x, y = i + direction[0], j + direction[1]
    #                     if x < grid.size and y < grid.size and grid.map[x][y] != 0:
    #                         uniformity -= abs(grid.map[i][j] - grid.map[x][y])
    #     return -uniformity 

    # def h_greedy(self, grid):
    #     max_tile = grid.getMaxTile()
    #     return max_tile
    
    # def h_merges(self, grid):
    #     merges = 0
    #     for i in range(grid.size):
    #         for j in range(grid.size - 1):
    #             if grid.map[i][j] == grid.map[i][j + 1]:
    #                 merges += 1
    #             if grid.map[j][i] == grid.map[j + 1][i]:
    #                 merges += 1
    #     return merges

    # def h_non_monotonic_penalty(self, grid):
    #     penalty = 0
    #     for i in range(grid.size):
    #         for j in range(grid.size - 1):
    #             if grid.map[i][j] > grid.map[i][j + 1]:
    #                 penalty += (grid.map[i][j] - grid.map[i][j + 1]) * (2 ** (grid.map[i][j] + grid.map[i][j + 1]))
    #             if grid.map[j][i] > grid.map[j + 1][i]:
    #                 penalty += (grid.map[j][i] - grid.map[j + 1][i]) * (2 ** (grid.map[j][i] + grid.map[j + 1][i]))
    #     return penalty
    
    def h_open_spot_next_to_2_or_4(self, grid):
        if len(grid.getAvailableCells()) != 1:
            return 0

        no_merges = True
        for i in range(grid.size):
            for j in range(grid.size - 1):
                if grid.map[i][j] == grid.map[i][j + 1] or grid.map[j][i] == grid.map[j + 1][i]:
                    no_merges = False
                    break
            if not no_merges:
                break

        if no_merges:
            open_cell = grid.getAvailableCells()[0]
            adjacent_cells = [
                (open_cell[0] + 1, open_cell[1]),
                (open_cell[0] - 1, open_cell[1]),
                (open_cell[0], open_cell[1] + 1),
                (open_cell[0], open_cell[1] - 1),
            ]
            score = 0
            
            for x, y in adjacent_cells:
                if 0 <= x < grid.size and 0 <= y < grid.size:
                    tile_value = grid.map[x][y]
                    if tile_value == 2 or tile_value == 4:
                        score += 1

            return score

        return 0
    
    def h_large_merges(self, grid):

        possible_mergers = 0

        for i in range(grid.size):
            for j in range(grid.size):
                tile_value = grid.map[i][j]

                if tile_value > 0:
                    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                    adj_tiles = [(i + di, j + dj) for di, dj in directions]

                    for a, b in adj_tiles:
                        if 0 <= a < grid.size and 0 <= b < grid.size:
                            neighbor_value = grid.map[a][b]

                            if neighbor_value == tile_value:
                                possible_mergers += 1

        return possible_mergers
    
    def h_top_corner(self, grid):
        max_tile = grid.getMaxTile()
        top_left_corner = grid.map[0][0]
        top_right_corner = grid.map[0][grid.size - 1]
        
        if top_left_corner == max_tile or top_right_corner == max_tile:
            return True
        else:
            return False

