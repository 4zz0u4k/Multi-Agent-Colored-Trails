import mesa
import numpy as np
import random
from abc import ABC, abstractmethod
from collections import defaultdict


class ColoredTrailsAgent(mesa.Agent):
    def __init__(self, model, strategy, start_pos, goal_pos):
        super().__init__(model)
        self.strategy = strategy
        self.pos = start_pos
        self.goal_pos = goal_pos
        self.coins = defaultdict(int)
        self.offers_made = []
        self.offers_received = []
        self.has_won = False
        self.last_position = start_pos
        self.turns_without_moving = 0
        # Give random starting coins
        colors = model.colors
        for _ in range(8):  # Each agent gets 8 random coins
            color = random.choice(colors)
            self.coins[color] += 1
    
    def step(self):
        if self.has_won:
            return
            
        # Phase 1: Generate offers
        new_offers = self.strategy.generate_offers(self)
        for offer in new_offers:
            self.model.add_offer(offer)
        
        # Phase 2: Try to move towards goal
        self.try_move_to_goal()
    
    def get_needed_colors(self):
        """Get colors needed for shortest path to goal"""
        path = self.model.get_shortest_path(self.pos, self.goal_pos)
        needed = defaultdict(int)
        
        for pos in path[1:]:  # Skip current position
            color = self.model.grid_colors[pos]
            needed[color] += 1
        
        # Return colors we don't have enough of
        missing = []
        for color, count in needed.items():
            if self.coins[color] < count:
                missing.extend([color] * (count - self.coins[color]))
        
        return missing
    
    def can_afford_path(self, path):
        """Check if agent has coins for given path"""
        needed = defaultdict(int)
        for pos in path[1:]:
            color = self.model.grid_colors[pos]
            needed[color] += 1
        
        for color, count in needed.items():
            if self.coins[color] < count:
                return False
        return True
    
    def spend_coins_for_path(self, path):
        """Spend coins to move along path"""
        for pos in path[1:]:
            color = self.model.grid_colors[pos]
            self.coins[color] -= 1
    
    def try_move_to_goal(self):
        """Try to move one step towards goal if possible"""
        old_pos = self.pos
        
        path = self.model.get_shortest_path(self.pos, self.goal_pos)
        if len(path) <= 1:  # Already at goal
            self.has_won = True
            return
        
        # Try to move just one step (next position in path)
        next_pos = path[1]  # First step toward goal
        color_needed = self.model.grid_colors[next_pos]
        
        if self.coins[color_needed] > 0:
            # Can afford this one step
            self.coins[color_needed] -= 1
            self.model.grid.move_agent(self, next_pos)
            
            if next_pos == self.goal_pos:
                self.has_won = True
        
        # Update stagnation tracking
        if self.pos == old_pos:
            self.turns_without_moving += 1
        else:
            self.turns_without_moving = 0
    
    def has_coins(self, coin_dict):
        """Check if agent has required coins"""
        for color, amount in coin_dict.items():
            if self.coins[color] < amount:
                return False
        return True
    
    def give_coins(self, coin_dict):
        """Remove coins from agent's inventory"""
        for color, amount in coin_dict.items():
            self.coins[color] -= amount
    
    def receive_coins(self, coin_dict):
        """Add coins to agent's inventory"""
        for color, amount in coin_dict.items():
            self.coins[color] += amount
