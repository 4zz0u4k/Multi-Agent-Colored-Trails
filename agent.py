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
        """Try to move towards goal if possible"""
        path = self.model.get_shortest_path(self.pos, self.goal_pos)
        
        if len(path) <= 1:  # Already at goal
            self.has_won = True
            return
        
        # Try progressively shorter paths
        for i in range(len(path), 0, -1):
            partial_path = path[:i]
            if self.can_afford_path(partial_path):
                self.spend_coins_for_path(partial_path)
                self.model.grid.move_agent(self, partial_path[-1])
                if partial_path[-1] == self.goal_pos:
                    self.has_won = True
                return
    
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
