import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

fastf1.plotting.setup_mpl()

# Load race
session = fastf1.get_session(2023, "Monaco", "R")
session.load()

driver = "VER"

laps = session.laps.pick_drivers(driver)

# Convert lap times to seconds
laps = laps[["LapNumber", "LapTime", "Compound"]].dropna()
laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()

# Remove outliers like pit laps
laps = laps[laps["LapTimeSeconds"] < laps["LapTimeSeconds"].quantile(0.95)]

# Fit degradation model (linear)
x = laps["LapNumber"]
y = laps["LapTimeSeconds"]

coefficients = np.polyfit(x, y, 1)
trend = np.poly1d(coefficients)

print("\nTyre degradation rate (sec per lap):", round(coefficients[0], 4))

# Predict optimal pit window
degradation_rate = coefficients[0]

if degradation_rate > 0.05:
    pit_window = int(laps["LapNumber"].median())
else:
    pit_window = int(laps["LapNumber"].max())

print("Suggested pit window around lap:", pit_window)

# Plot lap times
plt.figure(figsize=(10,5))

plt.scatter(x, y, label="Lap Times")

plt.plot(x, trend(x), linewidth=3, label="Degradation Trend")

plt.axvline(pit_window, linestyle="--", label="Suggested Pit Stop")

plt.xlabel("Lap Number")
plt.ylabel("Lap Time (seconds)")
plt.title(f"{driver} Tyre Degradation Analysis")
plt.legend()

plt.show()