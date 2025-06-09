import mesa
import numpy as np
import random
from abc import ABC, abstractmethod
from collections import defaultdict
from strategies import GreedyStrategy,CooperativeStrategy
from agent import ColoredTrailsAgent
class ColoredTrailsModel(mesa.Model):
    def __init__(self, width=5, height=5, num_agents=3):
        super().__init__()
        self.width = width
        self.height = height
        self.colors = ['red', 'blue', 'green', 'yellow']
        
        # Create grid and scheduler
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)
        
        # Initialize colored grid
        self.grid_colors = {}
        self.setup_colored_grid()
        
        # Create agents with different strategies
        self.offers_pool = []
        self.create_agents()
        self.agent_stuck = False
        # Data collection
        self.datacollector = mesa.DataCollector(
            agent_reporters={
                "Coins": lambda a: dict(a.coins),
                "Position": "pos",
                "HasWon": "has_won"
            }
        )
    
    def setup_colored_grid(self):
        """Assign random colors to each grid cell"""
        for x in range(self.width):
            for y in range(self.height):
                color = random.choice(self.colors)
                self.grid_colors[(x, y)] = color
    
    def create_agents(self):
        """Create agents with different strategies"""
        strategies = [GreedyStrategy(), CooperativeStrategy(), CooperativeStrategy()]
        
        # Define start and goal positions
        goal = (self.width-1, self.height-1)
        positions = [
            (self.width-1, 0),
            (0, self.height-1),
            (0, 0)
        ]
        
        for i in range(3):
            start_pos = positions[i]
            agent = ColoredTrailsAgent(self, strategies[i], start_pos, goal)
            self.schedule.add(agent)
            self.grid.place_agent(agent, start_pos)
    
    def get_shortest_path(self, start, goal):
        """Return path with only adjacent moves (Manhattan neighbors)"""
        path = [start]
        current = start
        
        while current != goal:
            x, y = current
            gx, gy = goal
            
            # Only move to adjacent cells (one step at a time)
            if abs(x - gx) + abs(y - gy) == 1:
                # Already adjacent to goal
                path.append(goal)
                break
            
            # Choose next adjacent cell toward goal
            possible_moves = []
            
            # Check all 4 adjacent directions
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                next_x, next_y = x + dx, y + dy
                
                # Check bounds
                if 0 <= next_x < self.width and 0 <= next_y < self.height:
                    # Calculate if this move gets us closer
                    current_distance = abs(x - gx) + abs(y - gy)
                    new_distance = abs(next_x - gx) + abs(next_y - gy)
                    
                    if new_distance < current_distance:
                        possible_moves.append((next_x, next_y))
            
            # Pick first valid move (or random if you want)
            if possible_moves:
                current = possible_moves[0]
                path.append(current)
            else:
                break  # Shouldn't happen with Manhattan distance
        
        return path
    
    def add_offer(self, offer):
        """Add trade offer to pool"""
        self.offers_pool.append(offer)
    
    def process_trades(self):
        """Process all trade offers"""
        for offer in self.offers_pool:
            from_agent = next(a for a in self.schedule.agents if a.unique_id == offer['from'])
            to_agent = next(a for a in self.schedule.agents if a.unique_id == offer['to'])
            
            # Check if both agents can complete trade
            if (from_agent.has_coins(offer['give']) and 
                to_agent.has_coins(offer['want']) and
                to_agent.strategy.evaluate_offer(to_agent, offer)):
                
                # Execute trade
                from_agent.give_coins(offer['give'])
                from_agent.receive_coins(offer['want'])
                to_agent.give_coins(offer['want'])
                to_agent.receive_coins(offer['give'])
        
        self.offers_pool = []  # Clear offers after processing
    
    def step(self):
        """Advance model by one step"""
        self.schedule.step()
        self.process_trades()
        for agent in self.schedule.agents:
            if agent.turns_without_moving >= 3:
                print(f"Game ended - Agent {agent.unique_id} stuck for 3 turns")
                self.agent_stuck = True
                return
        self.datacollector.collect(self)
        
    
    def get_winner(self):
        """Return winning agent if any"""
        for agent in self.schedule.agents:
            if agent.has_won:
                return agent
        return None
