import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.undercut_sim import simulate_undercut, simulate_overcut

deg_rate = 0.1

print("Undercut:", simulate_undercut(deg_rate))
print("Overcut:", simulate_overcut(deg_rate))