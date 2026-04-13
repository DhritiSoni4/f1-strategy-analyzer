import numpy as np
import pandas as pd
import json
import os
from scipy.optimize import curve_fit
from data_loader import load_session, get_driver_laps

PARAMS_PATH = os.path.join(os.path.dirname(__file__), "..", "deg_params.json")

# Races used to fit the model
TRAINING_RACES = [
    (2023, "Bahrain"),
    (2023, "Australia"),
    (2023, "Monaco"),
    (2023, "Silverstone"),
    (2023, "Monza"),
    (2023, "Abu Dhabi"),
]

# Fallback params if a compound has too little data to fit
FALLBACK_PARAMS = {
    "SOFT":         {"a": 0.08, "b": 1.2, "c": 0.0},
    "MEDIUM":       {"a": 0.04, "b": 1.1, "c": 0.0},
    "HARD":         {"a": 0.02, "b": 1.0, "c": 0.0},
    "INTERMEDIATE": {"a": 0.03, "b": 1.1, "c": 0.0},
    "WET":          {"a": 0.03, "b": 1.0, "c": 0.0},
}


def deg_model(lap_in_stint: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    """
    Degradation curve: predicted lap time delta (seconds) given lap in stint.
    delta = a * (lap_in_stint + 1)^b + c
    """
    return a * np.power(lap_in_stint + 1, b) + c


def collect_stint_deltas(year: int, race: str) -> pd.DataFrame:
    """
    For a given race, collect (LapInStint, LapTimeDelta, Compound) rows
    across all drivers. LapTimeDelta = lap_time - driver's median clean lap.
    """
    session = load_session(year, race)
    rows = []

    for driver in session.drivers:
        try:
            laps = get_driver_laps(session, driver)
        except Exception:
            continue

        if laps.empty:
            continue

        baseline = laps["LapTimeSeconds"].median()

        for _, row in laps.iterrows():
            delta = row["LapTimeSeconds"] - baseline
            # Only keep positive deltas (degradation) and reasonable range
            if 0 <= delta <= 10:
                rows.append({
                    "LapInStint": row["LapInStint"],
                    "LapTimeDelta": delta,
                    "Compound": row["Compound"],
                })

    return pd.DataFrame(rows)


def fit_all_compounds(save: bool = True) -> dict:
    """
    Fit degradation curve parameters per compound using TRAINING_RACES.
    Saves results to deg_params.json if save=True.
    Returns dict: { compound: {a, b, c} }
    """
    all_data = []
    for year, race in TRAINING_RACES:
        print(f"Loading {race} {year}...")
        try:
            df = collect_stint_deltas(year, race)
            all_data.append(df)
        except Exception as e:
            print(f"  Skipped: {e}")

    combined = pd.concat(all_data, ignore_index=True)
    params = {}

    for compound in ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]:
        data = combined[combined["Compound"] == compound]

        if len(data) < 20:
            print(f"  {compound}: not enough data, using fallback")
            params[compound] = FALLBACK_PARAMS[compound]
            continue

        try:
            popt, _ = curve_fit(
                deg_model,
                data["LapInStint"].values,
                data["LapTimeDelta"].values,
                p0=[0.04, 1.1, 0.0],
                bounds=([0, 0.5, -2], [2, 3, 5]),
                maxfev=10000,
            )
            params[compound] = {"a": round(popt[0], 5), "b": round(popt[1], 5), "c": round(popt[2], 5)}
            print(f"  {compound}: a={popt[0]:.4f}, b={popt[1]:.4f}, c={popt[2]:.4f}")
        except Exception as e:
            print(f"  {compound}: fit failed ({e}), using fallback")
            params[compound] = FALLBACK_PARAMS[compound]

    if save:
        with open(PARAMS_PATH, "w") as f:
            json.dump(params, f, indent=2)
        print(f"\nSaved to {PARAMS_PATH}")

    return params


def load_params() -> dict:
    """Load fitted params from disk, or use fallback if file doesn't exist."""
    if os.path.exists(PARAMS_PATH):
        with open(PARAMS_PATH) as f:
            return json.load(f)
    print("deg_params.json not found — using fallback params. Run fit_all_compounds() first.")
    return FALLBACK_PARAMS


def predict_lap_delta(compound: str, lap_in_stint: int, params: dict = None) -> float:
    """
    Predict how many seconds slower a lap is at `lap_in_stint` on a given compound.
    lap_in_stint=0 means the first lap on fresh tires.
    """
    if params is None:
        params = load_params()

    p = params.get(compound, FALLBACK_PARAMS.get(compound, FALLBACK_PARAMS["MEDIUM"]))
    return deg_model(lap_in_stint, p["a"], p["b"], p["c"])


def predict_stint_time(compound: str, num_laps: int, base_lap_time: float, params: dict = None) -> float:
    """
    Predict total stint time for `num_laps` on `compound` starting from fresh tires.
    base_lap_time: the driver's clean reference lap time in seconds.
    """
    if params is None:
        params = load_params()

    total = 0.0
    for lap in range(num_laps):
        total += base_lap_time + predict_lap_delta(compound, lap, params)
    return total


if __name__ == "__main__":
    print("Fitting degradation model across training races...")
    fit_all_compounds(save=True)