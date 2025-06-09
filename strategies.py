import mesa
import numpy as np
import random
from abc import ABC, abstractmethod
from collections import defaultdict


class Strategy(ABC):
    """Base strategy class that all strategies must inherit from"""
    
    @abstractmethod
    def generate_offers(self, agent):
        """Generate trade offers based on agent's current state"""
        pass
    
    @abstractmethod
    def evaluate_offer(self, agent, offer):
        """Evaluate incoming trade offer and return acceptance decision"""
        pass


class GreedyStrategy(Strategy):
    """Always tries to get coins for shortest path to goal"""
    
    def generate_offers(self, agent):
        offers = []
        needed_colors = agent.get_needed_colors()
        
        for color in needed_colors:
            for other_agent in agent.model.schedule.agents:
                if other_agent.unique_id != agent.unique_id:
                    # Offer random coin for needed color
                    for give_color, give_amount in agent.coins.items():
                        if give_amount > 0:
                            offer = {
                                'from': agent.unique_id,
                                'to': other_agent.unique_id,
                                'give': {give_color: 1},
                                'want': {color: 1}
                            }
                            offers.append(offer)
                            break
        return offers[:2]  # Limit offers per turn
    
    def evaluate_offer(self, agent, offer):
        needed_colors = agent.get_needed_colors()
        for color in offer['want']:
            if color in needed_colors:
                return True
        return False


class CooperativeStrategy(Strategy):
    """More willing to make trades that help others"""
    
    def generate_offers(self, agent):
        offers = []
        for other_agent in agent.model.schedule.agents:
            if other_agent.unique_id != agent.unique_id:
                other_needed = other_agent.get_needed_colors()
                
                for color in other_needed:
                    if agent.coins.get(color, 0) > 1:  # Only if we have extra
                        for give_color, give_amount in agent.coins.items():
                            if give_amount > 0:
                                offer = {
                                    'from': agent.unique_id,
                                    'to': other_agent.unique_id,
                                    'give': {color: 1},
                                    'want': {give_color: 1}
                                }
                                offers.append(offer)
                                break
        return offers[:1]  # Fewer offers than greedy
    
    def evaluate_offer(self, agent, offer):
        # Accept if we have extra coins or really need what's offered
        for color, amount in offer['give'].items():
            if agent.coins.get(color, 0) > 1:
                return True
        
        needed_colors = agent.get_needed_colors()
        for color in offer['want']:
            if color in needed_colors:
                return True
        return random.random() < 0.3  # Sometimes accept anyway
