import fastf1
import fastf1.plotting
import pandas as pd
import os

fastf1.plotting.setup_mpl()

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)


def load_session(year: int, race: str, session_type: str = "R"):
    """
    Load a FastF1 session with caching.
    session_type: "R" = Race, "Q" = Qualifying, "FP1/FP2/FP3"
    """
    session = fastf1.get_session(year, race, session_type)
    session.load()
    return session


def get_driver_laps(session, driver: str, remove_outliers: bool = True) -> pd.DataFrame:
    """
    Extract clean lap data for a driver from a loaded session.
    Returns DataFrame with LapNumber, LapTimeSeconds, Compound, Stint, LapInStint.
    """
    laps = session.laps.pick_drivers(driver)
    laps = laps[["LapNumber", "LapTime", "Compound", "Stint", "PitInTime"]].copy()
    laps = laps.dropna(subset=["LapTime", "Compound"])
    laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()

    if remove_outliers:
        laps = laps[laps["LapTimeSeconds"] < laps["LapTimeSeconds"].quantile(0.95)]
        laps = laps[laps["LapTimeSeconds"] > laps["LapTimeSeconds"].quantile(0.05)]

    # Compute lap number within each stint (starts at 0)
    laps["LapInStint"] = laps.groupby("Stint").cumcount()

    laps = laps.reset_index(drop=True)
    return laps


def get_actual_pit_laps(session, driver: str) -> list[int]:
    """
    Return the lap numbers on which a driver actually pitted.
    Uses PitInTime from FastF1 as ground truth.
    """
    laps = session.laps.pick_drivers(driver)
    pit_laps = laps[laps["PitInTime"].notna()]["LapNumber"].astype(int).tolist()
    return pit_laps