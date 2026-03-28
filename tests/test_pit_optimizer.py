import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.pit_optimizer import find_optimal_pit

result = find_optimal_pit(
    total_laps=30,
    deg_rate=0.1,
    gap_behind=10  # try different values
)

print("Optimal Strategy:", result)