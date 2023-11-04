import random
import math
from BaseAI import BaseAI

class IntelligentAgent(BaseAI):
    def __init__(self):
        self.depth_limit = 4  # or another number based on your testing
        
    def getMove(self, grid):
        alpha = float('-inf')
        beta = float('inf')
        best_move, _ = self.expectiminimax(grid, 0, True, alpha, beta)  # Assuming it's player's turn first
        return best_move

    def expectiminimax(self, grid, depth, maximizingPlayer, alpha, beta):
        if depth == self.depth_limit or not grid.canMove():
            return None, self.h1(grid)
        
        best_move = None
        if maximizingPlayer:
            max_eval = float('-inf')
            for move, new_grid in grid.getAvailableMoves():
                _, eval = self.expectiminimax(new_grid, depth+1, False, alpha, beta)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # alpha-beta pruning
            return best_move, max_eval
        else:  # chance node, assuming it's the computer's turn
            sum_eval = 0
            num_possible_moves = 0
            for move, new_grid in grid.getAvailableMoves():
                _, eval = self.expectiminimax(new_grid, depth+1, True, alpha, beta)
                sum_eval += eval
                num_possible_moves += 1
                if beta <= alpha:
                    break  # alpha-beta pruning
            avg_eval = sum_eval / num_possible_moves if num_possible_moves > 0 else 0
            return best_move, avg_eval

    def h_empty(self, grid):
        empty_cells = len(grid.getAvailableCells())
        return empty_cells
    
    def h_monotinicity(self, grid):
        # Calculating Monotonicity
        monotonicity = 0
        for i in range(grid.size):
            m = 0  # current monotonicity
            for j in range(grid.size - 1):
                if grid.map[i][j] >= grid.map[i][j + 1]:
                    m += 1
            monotonicity += m / (grid.size - 1)  # normalized to [0,1]
        
        return monotonicity
    
    def h_random(self, grid):
        return random.random()
    
    def h_uniformity(self, grid):
        uniformity = 0
        for i in range(grid.size):
            for j in range(grid.size):
                if grid.map[i][j] != 0:
                    for direction in [(0, 1), (1, 0)]:
                        x, y = i + direction[0], j + direction[1]
                        if x < grid.size and y < grid.size and grid.map[x][y] != 0:
                            uniformity -= abs(grid.map[i][j] - grid.map[x][y])
        return -uniformity  # return negative since lower uniformity (less difference between tiles) is better

    def h_greedy(self, grid):
        max_tile = grid.getMaxTile()
        return max_tile
    
    def h_merges(self, grid):
        merges = 0
        for i in range(grid.size):
            for j in range(grid.size - 1):
                # Horizontal merges
                if grid.map[i][j] == grid.map[i][j + 1]:
                    merges += 1
                # Vertical merges
                if grid.map[j][i] == grid.map[j + 1][i]:
                    merges += 1
        return merges

    def h_non_monotonic_penalty(self, grid):
        penalty = 0
        for i in range(grid.size):
            for j in range(grid.size - 1):
                # Horizontal penalty
                if grid.map[i][j] > grid.map[i][j + 1]:
                    penalty += (grid.map[i][j] - grid.map[i][j + 1]) * (2 ** (grid.map[i][j] + grid.map[i][j + 1]))
                # Vertical penalty
                if grid.map[j][i] > grid.map[j + 1][i]:
                    penalty += (grid.map[j][i] - grid.map[j + 1][i]) * (2 ** (grid.map[j][i] + grid.map[j + 1][i]))
        # print(str(penalty))
        return penalty


    def h1(self, grid):
        empty_score = self.h_empty(grid)
        monotonicity_score = self.h_monotinicity(grid)
        random_score = self.h_random(grid)
        non_mon_score = self.h_non_monotonic_penalty(grid)
        merges = self.h_merges(grid)
        # You can adjust the weights (1.0, 1.0, 1.0) to prioritize certain heuristics over others
        
        h1 = (
            empty_score * 3.0 +
            monotonicity_score * 2.0 +
            random_score * 1.0 +
            # non_mon_score * 1.0
            merges * 2.0
        )

        return h1
    
    def h2(self, grid):
        empty_score = self.h_empty(grid)
        monotonicity_score = self.h_monotinicity(grid)
        uniformity_score = self.h_uniformity(grid)
        greedy_score = self.h_greedy(grid)
        random_score = self.h_random(grid)
        # You can adjust the weights (1.0, 1.0, 1.0) to prioritize certain heuristics over others
        
        h2 = (
            empty_score * 5.0 +
            monotonicity_score * 4.0 +
            uniformity_score * 3.0 +
            greedy_score * 2.0 +
            random_score * 1.0

        )

        return h2



# def heuristic(self, grid):
#         # empty_weight = 1.0
#         # max_tile_weight = 0.0
#         # monotonicity_weight = 1.0
#         # smoothness_weight = 5.0
#         # clustering_weight = 1.0
#         # corner_weight = 1.0

        

#         # empty_cells = len(grid.getAvailableCells())
#         # max_tile = grid.getMaxTile()
    
        

#         # # Calculating Smoothness
#         # smoothness = 0
#         # for i in range(grid.size):
#         #     for j in range(grid.size):
#         #         if grid.map[i][j] != 0:
#         #             for direction in [(0, 1), (1, 0)]:
#         #                 x, y = i + direction[0], j + direction[1]
#         #                 if x < grid.size and y < grid.size and grid.map[x][y] != 0:
#         #                     smoothness -= abs(math.log2(grid.map[i][j]) - math.log2(grid.map[x][y]))

#         # # Calculating Clustering
#         # clustering = 0
#         # for i in range(grid.size):
#         #     for j in range(grid.size):
#         #         if grid.map[i][j] != 0:
#         #             neighbors_sum = 0
#         #             count = 0
#         #             for direction in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
#         #                 x, y = i + direction[0], j + direction[1]
#         #                 if x >= 0 and x < grid.size and y >= 0 and y < grid.size and grid.map[x][y] != 0:
#         #                     neighbors_sum += abs(math.log2(grid.map[i][j]) - math.log2(grid.map[x][y]))
#         #                     count += 1
#         #             if count > 0:
#         #                 clustering -= neighbors_sum / count

#         # corner_bonus = 0
#         # corner_indices = [(0, 0), (0, grid.size - 1), (grid.size - 1, 0), (grid.size - 1, grid.size - 1)]
#         # for i, j in corner_indices:
#         #     if grid.map[i][j] == max_tile:
#         #         corner_bonus = max_tile

#         # # Weighted sum of factors
#         # heuristic_value = (
#         #     empty_weight * empty_cells +
#         #     max_tile_weight * math.log2(max_tile) +
#         #     monotonicity_weight * monotonicity +
#         #     smoothness_weight * smoothness + clustering_weight * clustering # +
#         #     # corner_weight * corner_bonus
            
#         # )

#         # if max_tile >= 2048:
#         #     heuristic_value += 10000

#         # # if grid.map[0][0] == max_tile or grid.map[0][3] == max_tile or grid.map[3][0] == max_tile or grid.map[3][3] == max_tile:
#         # #     heuristic_value += 500  # arbitrary reward value

#         # # merging_opportunities = 0
#         # # for i in range(grid.size):
#         # #     for j in range(grid.size - 1):
#         # #         if grid.map[i][j] == grid.map[i][j + 1]:
#         # #             merging_opportunities += 1
#         # # heuristic_value += 50 * merging_opportunities  # arbitrary reward value

#         # # corner_bonus = 0
#         # # if grid.map[0][0] == max_tile or grid.map[0][3] == max_tile or grid.map[3][0] == max_tile or grid.map[3][3] == max_tile:
#         # #     corner_bonus = 25  # or some other weight value
#         # # heuristic_value += corner_bonus

#         empty_score = self.h_empty(grid)
#         monotonicity_score = self.h_monotinicity(grid)
#         random_score = self.h_random(grid)
#         # You can adjust the weights (1.0, 1.0, 1.0) to prioritize certain heuristics over others
#         return 1.0 * empty_score + 1.0 * monotonicity_score + 1.0 * random_score

        
#         # return heuristic_value
