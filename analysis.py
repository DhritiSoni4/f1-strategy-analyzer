import fastf1
import matplotlib.pyplot as plt
import pandas as pd

fastf1.Cache.enable_cache('./cache')

session = fastf1.get_session(2024, "Monaco", "R")
session.load()

ver_laps = session.laps.pick_drivers("VER")
ham_laps = session.laps.pick_drivers("HAM")

# convert lap times
ver_times = ver_laps['LapTime'].dt.total_seconds().reset_index(drop=True)
ham_times = ham_laps['LapTime'].dt.total_seconds().reset_index(drop=True)

# calculate delta
delta = ham_times - ver_times

laps = range(1, len(delta)+1)

plt.figure(figsize=(10,5))
plt.plot(laps, delta)

plt.axhline(0)

plt.xlabel("Lap Number")
plt.ylabel("Time Difference (Hamilton - Verstappen)")
plt.title("Lap Time Delta: HAM vs VER - Monaco GP")

plt.show()