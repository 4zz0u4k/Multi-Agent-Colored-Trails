import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import to_rgba
import numpy as np


class ColoredTrailsViz:
    def __init__(self, model):
        self.model = model
        self.color_map = {
            'red': '#FF4444',
            'blue': '#4444FF', 
            'green': '#44FF44',
            'yellow': '#FFFF44'
        }
        
    def visualize_step(self, step_num=None):
        """Show current game state"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Left: Grid with agents
        self._draw_grid(ax1)
        
        # Right: Agent coin inventories
        self._draw_inventories(ax2)
        
        title = f"Colored Trails - Step {step_num}" if step_num else "Colored Trails"
        fig.suptitle(title, fontsize=16)
        plt.tight_layout()
        plt.savefig(f'steps_viz/game_step_{step_num}.png')
        plt.close()
    
    def _draw_grid(self, ax):
        """Draw the colored grid with agent positions"""
        width, height = self.model.width, self.model.height
        
        # Draw colored cells
        for x in range(width):
            for y in range(height):
                color = self.model.grid_colors[(x, y)]
                rect = patches.Rectangle((x, y), 1, 1, 
                                       facecolor=self.color_map[color],
                                       alpha=0.6, edgecolor='black')
                ax.add_patch(rect)
        
        # Draw agents
        for agent in self.model.schedule.agents:
            x, y = agent.pos
            circle = patches.Circle((x + 0.5, y + 0.5), 0.3,
                                  facecolor='white', edgecolor='black', linewidth=2)
            ax.add_patch(circle)
            
            # Agent ID
            ax.text(x + 0.5, y + 0.5, str(agent.unique_id),
                   ha='center', va='center', fontweight='bold', fontsize=12)
            
            # Goal marker
            gx, gy = agent.goal_pos
            goal_marker = patches.Rectangle((gx + 0.3, gy + 0.3), 0.4, 0.4,
                                          facecolor='gold', edgecolor='black',
                                          linewidth=2)
            ax.add_patch(goal_marker)
        
        
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)
        ax.set_aspect('equal')
        ax.set_title('Game Board')
        ax.grid(True, alpha=0.3)
    
    def _draw_inventories(self, ax):
        """Draw agent coin inventories as bar chart"""
        agents = list(self.model.schedule.agents)
        colors = list(self.color_map.keys())
        
        # Prepare data
        agent_ids = [f"Agent {a.unique_id}" for a in agents]
        coin_data = np.zeros((len(agents), len(colors)))
        
        for i, agent in enumerate(agents):
            for j, color in enumerate(colors):
                coin_data[i, j] = agent.coins.get(color, 0)
        
        # Create stacked bar chart
        bottom = np.zeros(len(agents))
        bar_colors = [self.color_map[color] for color in colors]
        
        for j, color in enumerate(colors):
            ax.bar(agent_ids, coin_data[:, j], bottom=bottom,
                  color=bar_colors[j], label=color.capitalize(), alpha=0.8)
            bottom += coin_data[:, j]
        
        # Add win status
        for i, agent in enumerate(agents):
            if agent.has_won:
                ax.text(i, bottom[i] + 0.5, '★ WON', ha='center', va='bottom',
                       fontweight='bold', color='gold', fontsize=12)
        
        ax.set_ylabel('Number of Coins')
        ax.set_title('Agent Inventories')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3, axis='y')
    
    def animate_game(self, max_steps=50):
        """Run game step by step with visualization"""
        print("Starting game animation...")
        step = 0
        
        while step < max_steps:
            print(f"\n--- Step {step} ---")
            self.visualize_step(step)
            
            # Check for winner
            winner = self.model.get_winner()
            if winner:
                print(f"Game Over! Agent {winner.unique_id} wins!")
                break
            
            # Wait for user input
            input("Press Enter for next step (or Ctrl+C to quit)...")
            
            # Advance model
            self.model.step()
            step += 1
        
        print("Game finished!")
    
    def print_game_summary(self):
        """Print text summary of current state"""
        print("\n=== GAME SUMMARY ===")
        for agent in self.model.schedule.agents:
            status = "WON" if agent.has_won else "Playing"
            coins_str = ", ".join([f"{color}:{count}" for color, count in agent.coins.items() if count > 0])
            print(f"Agent {agent.unique_id} [{status}]: Pos{agent.pos}→Goal{agent.goal_pos} | Coins: {coins_str}")