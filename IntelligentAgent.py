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
            return None, self.heuristic(grid)
        
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

    def heuristic(self, grid):
        empty_weight = 1.0
        max_tile_weight = 1.0
        monotonicity_weight = 1.0
        smoothness_weight = 1.0
        clustering_weight = 1.0

        empty_cells = len(grid.getAvailableCells())
        max_tile = grid.getMaxTile()
    
        # Calculating Monotonicity
        monotonicity = 0
        for i in range(grid.size):
            m = 0  # current monotonicity
            for j in range(grid.size - 1):
                if grid.map[i][j] >= grid.map[i][j + 1]:
                    m += 1
            monotonicity += m / (grid.size - 1)  # normalized to [0,1]

        # Calculating Smoothness
        smoothness = 0
        for i in range(grid.size):
            for j in range(grid.size):
                if grid.map[i][j] != 0:
                    for direction in [(0, 1), (1, 0)]:
                        x, y = i + direction[0], j + direction[1]
                        if x < grid.size and y < grid.size and grid.map[x][y] != 0:
                            smoothness -= abs(math.log2(grid.map[i][j]) - math.log2(grid.map[x][y]))

        # Calculating Clustering
        clustering = 0
        for i in range(grid.size):
            for j in range(grid.size):
                if grid.map[i][j] != 0:
                    neighbors_sum = 0
                    count = 0
                    for direction in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        x, y = i + direction[0], j + direction[1]
                        if x >= 0 and x < grid.size and y >= 0 and y < grid.size and grid.map[x][y] != 0:
                            neighbors_sum += abs(math.log2(grid.map[i][j]) - math.log2(grid.map[x][y]))
                            count += 1
                    if count > 0:
                        clustering -= neighbors_sum / count

        # Weighted sum of factors
        heuristic_value = (
            empty_weight * empty_cells +
            max_tile_weight * math.log2(max_tile) +
            monotonicity_weight * monotonicity +
            smoothness_weight * smoothness +
            clustering_weight * clustering
        )
        
        return heuristic_value
