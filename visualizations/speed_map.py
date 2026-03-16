import fastf1
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np

fastf1.Cache.enable_cache('./cache')

session = fastf1.get_session(2024, "Monaco", "Q")
session.load()

laps = session.laps.pick_drivers("VER")
fastest_lap = laps.pick_fastest()

# merge car telemetry with position telemetry
telemetry = fastest_lap.get_telemetry()

x = telemetry['X']
y = telemetry['Y']
speed = telemetry['Speed']

points = np.array([x, y]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)

plt.figure(figsize=(8,8))

lc = LineCollection(segments, cmap='plasma', linewidth=3)
lc.set_array(speed)

plt.gca().add_collection(lc)

plt.axis('equal')
plt.title("Speed Map - Verstappen Fastest Lap (Monaco)")
plt.colorbar(lc, label="Speed (km/h)")
plt.axis("off")
plt.gca().set_facecolor("black")
plt.show()