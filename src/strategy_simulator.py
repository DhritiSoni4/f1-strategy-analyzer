import fastf1
import fastf1.plotting
import pandas as pd
import numpy as np

fastf1.plotting.setup_mpl()

# Load session
session = fastf1.get_session(2023, "Monaco", "R")
session.load()

driver = "VER"

laps = session.laps.pick_drivers(driver)

# Clean data
laps = laps[["LapNumber", "LapTime", "Compound"]].dropna()
laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()

# Remove extreme outliers (pit laps, safety car)
laps = laps[laps["LapTimeSeconds"] < laps["LapTimeSeconds"].quantile(0.95)]

# ----------------------------
# ORIGINAL STRATEGY TIME
# ----------------------------
original_total_time = laps["LapTimeSeconds"].sum()

# ----------------------------
# SIMULATED STRATEGY
# ----------------------------

# Example: simulate earlier pit stop
pit_lap = 35  # try different values

# Split race into two stints
stint1 = laps[laps["LapNumber"] <= pit_lap]
stint2 = laps[laps["LapNumber"] > pit_lap]

# Assume fresh tyres improve lap time slightly
improvement_factor = 0.98  # 2% faster after pit

stint2_simulated = stint2["LapTimeSeconds"] * improvement_factor

simulated_total_time = stint1["LapTimeSeconds"].sum() + stint2_simulated.sum()

# ----------------------------
# RESULTS
# ----------------------------

print(f"\nDriver: {driver}")
print(f"Pit Lap Simulated: {pit_lap}")

print("\nOriginal Strategy Time:", round(original_total_time, 2), "sec")
print("Simulated Strategy Time:", round(simulated_total_time, 2), "sec")

delta = original_total_time - simulated_total_time

if delta > 0:
    print(f"\n✅ Better to pit earlier by ~{round(delta,2)} seconds")
else:
    print(f"\n❌ Current strategy is better by ~{round(abs(delta),2)} seconds")