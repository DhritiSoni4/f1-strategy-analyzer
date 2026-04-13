import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from data_loader import load_session, get_driver_laps
from tire_model import predict_stint_time, load_params

# Pit stop time loss per circuit (stationary + in/out lap delta), in seconds
PIT_LOSS = {
    "monaco":      24.5,
    "singapore":   23.0,
    "hungary":     22.5,
    "bahrain":     21.0,
    "silverstone": 20.5,
    "monza":       19.0,
    "default":     22.0,
}


def get_pit_loss(circuit: str) -> float:
    return PIT_LOSS.get(circuit.lower(), PIT_LOSS["default"])


def optimize_pit_window(
    session,
    driver: str,
    circuit: str,
    compound_after_pit: str = "MEDIUM",
    min_pit_lap: int = 8,
    params: dict = None,
) -> pd.DataFrame:
    """
    Find the optimal pit lap for a one-stop strategy.

    Returns a DataFrame with columns [PitLap, TotalTime] for all
    evaluated pit windows, sorted by TotalTime ascending.
    """
    if params is None:
        params = load_params()

    laps = get_driver_laps(session, driver)
    if laps.empty:
        raise ValueError(f"No clean lap data found for driver {driver}")

    base_lap_time = laps["LapTimeSeconds"].median()
    total_laps = int(laps["LapNumber"].max())
    pit_loss = get_pit_loss(circuit)

    results = []

    for pit_lap in range(min_pit_lap, total_laps - 5):
        # Stint 1: actual recorded lap times up to pit lap
        stint1_laps = laps[laps["LapNumber"] <= pit_lap]["LapTimeSeconds"].values
        stint1_time = stint1_laps.sum()

        # Stint 2: predicted from tire model on fresh compound after pit
        stint2_laps = total_laps - pit_lap
        stint2_time = predict_stint_time(
            compound=compound_after_pit,
            num_laps=stint2_laps,
            base_lap_time=base_lap_time,
            params=params,
        )

        total_time = stint1_time + pit_loss + stint2_time
        results.append({"PitLap": pit_lap, "TotalTime": total_time})

    results_df = pd.DataFrame(results).sort_values("TotalTime").reset_index(drop=True)
    return results_df


def get_best_pit_lap(results_df: pd.DataFrame) -> dict:
    """Return the optimal pit lap and its predicted total time."""
    best = results_df.iloc[0]
    return {"pit_lap": int(best["PitLap"]), "total_time": round(best["TotalTime"], 2)}


def plot_pit_window(results_df: pd.DataFrame, driver: str, circuit: str):
    """Plot the optimization curve."""
    best = get_best_pit_lap(results_df)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(results_df["PitLap"], results_df["TotalTime"], color="steelblue", linewidth=2)
    ax.scatter(best["pit_lap"], best["total_time"], color="red", zorder=5, s=80)
    ax.axvline(best["pit_lap"], linestyle="--", color="red", alpha=0.6)
    ax.set_xlabel("Pit Lap")
    ax.set_ylabel("Predicted Total Race Time (s)")
    ax.set_title(f"{driver} – Optimal Pit Window | {circuit}")
    ax.annotate(
        f"Optimal: Lap {best['pit_lap']}",
        xy=(best["pit_lap"], best["total_time"]),
        xytext=(best["pit_lap"] + 2, best["total_time"] + 5),
        arrowprops=dict(arrowstyle="->"),
        fontsize=10,
    )
    plt.tight_layout()
    return fig


if __name__ == "__main__":
    session = load_session(2023, "Monaco")
    driver = "VER"

    results = optimize_pit_window(session, driver, circuit="monaco")
    best = get_best_pit_lap(results)

    print(f"\nDriver: {driver}")
    print(f"Optimal Pit Lap: {best['pit_lap']}")
    print(f"Predicted Total Time: {best['total_time']} sec")

    fig = plot_pit_window(results, driver, "Monaco 2023")
    plt.show()