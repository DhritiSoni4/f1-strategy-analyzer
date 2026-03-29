import numpy as np
from scipy.optimize import curve_fit

def degradation_model(lap, a, b):
    return a * lap + b

def fit_tire_degradation(laps, lap_times):
    # Convert to numpy arrays
    laps = np.array(laps)
    lap_times = np.array(lap_times)

    # Normalize lap times (important)
    lap_times = lap_times - lap_times[0]

    # Fit curve
    params, _ = curve_fit(degradation_model, laps, lap_times)

    a, b = params

    return {
        "deg_rate": float(abs(a)),
        "baseline": float(b)
    }

laps = [1,2,3,4,5,6]
lap_times = [90, 90.3, 90.7, 91.2, 91.8, 92.5]

print(fit_tire_degradation(laps, lap_times))