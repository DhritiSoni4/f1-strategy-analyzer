import fastf1
import fastf1.plotting
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

fastf1.plotting.setup_mpl()

session = fastf1.get_session(2023, "Monaco", "R")
session.load()

driver = "VER"

laps = session.laps.pick_drivers(driver)

# Clean data
laps = laps[["LapNumber", "LapTime", "Compound"]].dropna()
laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()

# Remove outliers
laps = laps[laps["LapTimeSeconds"] < laps["LapTimeSeconds"].quantile(0.95)]

original_time = laps["LapTimeSeconds"].sum()

# Compound-based degradation
compound_deg = {
    "SOFT": 0.05,
    "MEDIUM": 0.03,
    "HARD": 0.02,
    "INTERMEDIATE": 0.025,
    "WET": 0.03
}

results = []

def simulate_stint(lap_times, compounds, after_pit=False):
    total = 0

    for i, (lap, comp) in enumerate(zip(lap_times, compounds)):
        base_deg = compound_deg.get(comp, 0.03)

        # non-linear degradation
        degradation = base_deg * (i ** 1.2)

        if after_pit:
            lap_time = lap * 0.97 + degradation
        else:
            lap_time = lap + degradation

        total += lap_time

    return total


for pit_lap in range(10, int(laps["LapNumber"].max()) - 5):

    stint1 = laps[laps["LapNumber"] <= pit_lap]
    stint2 = laps[laps["LapNumber"] > pit_lap]

    stint1_time = simulate_stint(
        stint1["LapTimeSeconds"].values,
        stint1["Compound"].values
    )

    stint2_time = simulate_stint(
        stint2["LapTimeSeconds"].values,
        stint2["Compound"].values,
        after_pit=True
    )

    total_time = stint1_time + stint2_time

    results.append((pit_lap, total_time))


results_df = pd.DataFrame(results, columns=["PitLap", "TotalTime"])

best_row = results_df.loc[results_df["TotalTime"].idxmin()]
best_lap = int(best_row["PitLap"])
best_time = best_row["TotalTime"]

gain = original_time - best_time

print(f"\nDriver: {driver}")
print(f"Original Time: {round(original_time,2)} sec")
print(f"\n🏁 Optimal Pit Lap: {best_lap}")
print(f"Optimal Strategy Time: {round(best_time,2)} sec")
print(f"\n🚀 Time Gain: {round(gain,2)} sec")

# Plot
plt.figure(figsize=(10,5))
plt.plot(results_df["PitLap"], results_df["TotalTime"])
plt.scatter(best_lap, best_time)
plt.axvline(best_lap, linestyle="--")

plt.xlabel("Pit Lap")
plt.ylabel("Total Time")
plt.title(f"{driver} Optimal Strategy")

plt.show()