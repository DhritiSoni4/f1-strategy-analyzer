import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import fastf1
import numpy as np
from models.tire_deg import fit_tire_degradation

# Enable cache (important)
fastf1.Cache.enable_cache('cache')

# Load session
session = fastf1.get_session(2023, 'Bahrain', 'R')
session.load()

# Pick a driver (change if you want)
driver = session.laps.pick_driver('VER')

# Pick ONE stint only
stint = driver[driver['Stint'] == 1]

# Clean data
stint = stint.dropna(subset=['LapTime'])

# Extract laps + times
laps = stint['LapNumber'].values
lap_times = stint['LapTime'].dt.total_seconds().values

# Normalize lap numbers (start from 1)
laps = laps - laps[0] + 1

result = fit_tire_degradation(laps, lap_times)

print("Degradation Result:", result)