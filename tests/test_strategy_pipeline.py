import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import fastf1
from models.tire_deg import fit_tire_degradation
from models.pit_optimizer import find_optimal_pit

# Enable cache
fastf1.Cache.enable_cache('cache')

# Load race
session = fastf1.get_session(2023, 'Bahrain', 'R')
session.load()

# Pick driver
driver = session.laps.pick_driver('VER')

# Pick stint
stint = driver[driver['Stint'] == 1]
stint = stint.dropna(subset=['LapTime'])

# Extract data
laps = stint['LapNumber'].values
lap_times = stint['LapTime'].dt.total_seconds().values

# Normalize laps
laps = laps - laps[0] + 1

# Step 1: get degradation
deg_result = fit_tire_degradation(laps, lap_times)
deg_rate = deg_result["deg_rate"]

# Step 2: estimate remaining laps (simple assumption)
total_laps = 30  # assume remaining

# Step 3: optimize pit
strategy = find_optimal_pit(total_laps, deg_rate)

print("Degradation:", deg_result)
print("Optimal Strategy:", strategy)