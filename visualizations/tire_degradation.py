import fastf1
import matplotlib.pyplot as plt

fastf1.Cache.enable_cache('./cache')

# load race session
session = fastf1.get_session(2024, "Monaco", "R")
session.load()

# choose driver
driver = "HAM"

laps = session.laps.pick_drivers(driver)

# remove pit laps because they distort lap times
laps = laps[~laps['PitInTime'].notna()]
laps = laps[~laps['PitOutTime'].notna()]

lap_numbers = laps['LapNumber']
lap_times = laps['LapTime'].dt.total_seconds()

plt.figure(figsize=(10,5))

plt.scatter(lap_numbers, lap_times)

plt.xlabel("Lap Number")
plt.ylabel("Lap Time (seconds)")
plt.title(f"Tire Degradation - {driver} (Monaco GP)")

plt.show()