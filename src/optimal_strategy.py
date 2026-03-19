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
laps = laps[["LapNumber", "LapTime"]].dropna()
laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()

# Remove outliers
laps = laps[laps["LapTimeSeconds"] < laps["LapTimeSeconds"].quantile(0.95)]

# Original time
original_time = laps["LapTimeSeconds"].sum()

# Store results
results = []

# Try multiple pit laps
for pit_lap in range(10, int(laps["LapNumber"].max()) - 5):

    stint1 = laps[laps["LapNumber"] <= pit_lap]
    stint2 = laps[laps["LapNumber"] > pit_lap]

    # simulate fresh tyres
    improvement_factor = 0.98
    stint2_time = (stint2["LapTimeSeconds"] * improvement_factor).sum()

    total_time = stint1["LapTimeSeconds"].sum() + stint2_time

    results.append((pit_lap, total_time))

# Convert to dataframe
results_df = pd.DataFrame(results, columns=["PitLap", "TotalTime"])

# Find best strategy
best_row = results_df.loc[results_df["TotalTime"].idxmin()]

best_lap = int(best_row["PitLap"])
best_time = best_row["TotalTime"]

print(f"\nDriver: {driver}")
print(f"Original Time: {round(original_time,2)} sec")

print(f"\n🏁 Optimal Pit Lap: {best_lap}")
print(f"Optimal Strategy Time: {round(best_time,2)} sec")

gain = original_time - best_time

print(f"\n🚀 Time Gain: {round(gain,2)} sec")