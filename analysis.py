import fastf1
import matplotlib.pyplot as plt

fastf1.Cache.enable_cache('./cache')

# load race
session = fastf1.get_session(2024, "Monaco", "R")
session.load()

# get laps for two drivers
ver_laps = session.laps.pick_drivers("VER")
ham_laps = session.laps.pick_drivers("HAM")

# convert lap times
ver_times = ver_laps['LapTime'].dt.total_seconds()
ham_times = ham_laps['LapTime'].dt.total_seconds()

plt.figure(figsize=(10,5))

plt.plot(ver_laps['LapNumber'], ver_times, label="Verstappen")
plt.plot(ham_laps['LapNumber'], ham_times, label="Hamilton")

plt.xlabel("Lap Number")
plt.ylabel("Lap Time (seconds)")
plt.title("Driver Pace Comparison - Monaco GP")

plt.legend()

plt.show()