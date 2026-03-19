import fastf1
import fastf1.plotting
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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

results = []

# Try multiple pit laps
for pit_lap in range(10, int(laps["LapNumber"].max()) - 5):

    stint1 = laps[laps["LapNumber"] <= pit_lap]
    stint2 = laps[laps["LapNumber"] > pit_lap]

    improvement_factor = 0.98
    stint2_time = (stint2["LapTimeSeconds"] * improvement_factor).sum()

    total_time = stint1["LapTimeSeconds"].sum() + stint2_time

    results.append((pit_lap, total_time))

# DataFrame
results_df = pd.DataFrame(results, columns=["PitLap", "TotalTime"])

# Best strategy
best_row = results_df.loc[results_df["TotalTime"].idxmin()]
best_lap = int(best_row["PitLap"])
best_time = best_row["TotalTime"]

gain = original_time - best_time

# -----------------------
# PRINT RESULTS
# -----------------------
print(f"\nDriver: {driver}")
print(f"Original Time: {round(original_time,2)} sec")

print(f"\n🏁 Optimal Pit Lap: {best_lap}")
print(f"Optimal Strategy Time: {round(best_time,2)} sec")

print(f"\n🚀 Time Gain: {round(gain,2)} sec")

# -----------------------
# PLOT OPTIMIZATION CURVE
# -----------------------

plt.figure(figsize=(10,5))

plt.plot(results_df["PitLap"], results_df["TotalTime"], label="Strategy Curve")

# highlight optimal point
plt.scatter(best_lap, best_time, s=100, label="Optimal Point")

plt.axvline(best_lap, linestyle="--", label=f"Best Lap = {best_lap}")

plt.xlabel("Pit Lap")
plt.ylabel("Total Race Time (seconds)")
plt.title(f"{driver} Optimal Pit Strategy Analysis")

plt.legend()
plt.show()