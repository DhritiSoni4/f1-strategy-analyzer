import fastf1
import matplotlib.pyplot as plt

fastf1.Cache.enable_cache('./cache')

session = fastf1.get_session(2024, "Monaco", "R")
session.load()

driver_laps = session.laps.pick_drivers("VER")

lap_times = driver_laps['LapTime'].dt.total_seconds()

plt.figure(figsize=(10,5))
plt.plot(driver_laps['LapNumber'], lap_times)

plt.xlabel("Lap Number")
plt.ylabel("Lap Time (seconds)")
plt.title("Max Verstappen Lap Times - Monaco GP")

plt.show()