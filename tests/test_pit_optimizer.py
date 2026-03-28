import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.pit_optimizer import find_optimal_pit

result = find_optimal_pit(total_laps=30, deg_rate=0.1)

print("Optimal Strategy:", result)