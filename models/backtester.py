import fastf1
import numpy as np
from models.tire_deg import fit_tire_degradation
from models.pit_optimizer import find_optimal_pit

fastf1.Cache.enable_cache('cache')


def get_actual_pit_lap(driver_laps):
    # Pit occurs when stint changes
    stints = driver_laps['Stint'].values
    
    for i in range(1, len(stints)):
        if stints[i] != stints[i - 1]:
            return driver_laps.iloc[i]['LapNumber']
    
    return None


def evaluate_race(year, race, driver_code='VER'):
    session = fastf1.get_session(year, race, 'R')
    session.load()

    laps = session.laps.pick_driver(driver_code)
    laps = laps.dropna(subset=['LapTime'])

    # Use first stint
    stint = laps[laps['Stint'] == 1]

    # 🚨 CRITICAL: only use early laps (simulate real-time prediction)
    stint = stint.iloc[3:12]

    stint = stint.dropna(subset=['LapTime'])

    lap_numbers = stint['LapNumber'].values
    lap_times = stint['LapTime'].dt.total_seconds().values

    # Normalize laps
    lap_numbers = lap_numbers - lap_numbers[0] + 1

    # Get degradation
    deg = fit_tire_degradation(lap_numbers, lap_times)
    deg_rate = deg["deg_rate"]

    # ✅ REAL remaining laps
    race_total_laps = laps['LapNumber'].max()
    current_lap = stint['LapNumber'].iloc[-1]

    total_laps = int(race_total_laps - current_lap)

    # Predict
    pred = find_optimal_pit(total_laps, deg_rate, gap_behind=20)
    predicted_lap = current_lap + pred["optimal_pit_lap"]

    
    # Actual
    actual_lap = get_actual_pit_lap(laps)

    if actual_lap is None:
        return None
    print("Deg rate:", deg_rate)
    print("Current lap:", current_lap)
    print("Remaining laps:", total_laps)
    print("Actual pit:", actual_lap)
    print("Predicted:", predicted_lap)


    error = abs(predicted_lap - actual_lap)

    return {
        "race": race,
        "predicted": predicted_lap,
        "actual": actual_lap,
        "error": error
    }