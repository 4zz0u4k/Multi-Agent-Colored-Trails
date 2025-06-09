from model import ColoredTrailsModel
from vizualisation import ColoredTrailsViz
def run_game(steps=50):
    """Run a game and return results"""
    model = ColoredTrailsModel()
    viz = ColoredTrailsViz(model)
    
    # Show initial state
    viz.visualize_step(0)
    
    for i in range(1, steps):
        model.step()
        viz.visualize_step(i)  # Show AFTER step
        
        winner = model.get_winner()
        if winner:
            print(f"Game ended at step {i}! Agent {winner.unique_id} won!")
            break
        elif model.agent_stuck:
            break
    else:
        print(f"Game ended after {steps} steps with no winner")
    
    return model

def print_game_state(model):
    """Print current game state"""
    print("\n=== GAME STATE ===")
    print(f"Grid colors: {model.grid_colors}")
    
    for agent in model.schedule.agents:
        print(f"\nAgent {agent.unique_id}:")
        print(f"  Position: {agent.pos} -> Goal: {agent.goal_pos}")
        print(f"  Coins: {dict(agent.coins)}")
        print(f"  Strategy: {agent.strategy.__class__.__name__}")
        print(f"  Won: {agent.has_won}")

# Run example
if __name__ == "__main__":
    model = run_game()
    print_game_state(model)