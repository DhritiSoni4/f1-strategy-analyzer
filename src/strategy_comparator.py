import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
from data_loader import load_session, get_driver_laps

COMPOUND_COLORS = {
    "SOFT":         "#E8002D",
    "MEDIUM":       "#FFF200",
    "HARD":         "#EBEBEB",
    "INTERMEDIATE": "#39B54A",
    "WET":          "#0067FF",
    "UNKNOWN":      "#999999",
}


def get_stint_summary(session, driver: str) -> pd.DataFrame:
    """
    Returns a DataFrame of stints for a driver:
    columns: Stint, Compound, StartLap, NumLaps
    """
    laps = get_driver_laps(session, driver, remove_outliers=False)
    stints = (
        laps.groupby(["Stint", "Compound"])
        .agg(StartLap=("LapNumber", "min"), NumLaps=("LapNumber", "count"))
        .reset_index()
        .sort_values("StartLap")
    )
    return stints


def plot_strategy_comparison(session, drivers: list[str], title: str = None):
    """
    Horizontal bar chart showing tyre strategy for each driver across the race.
    """
    fig, ax = plt.subplots(figsize=(12, max(3, len(drivers) * 0.8)))

    for i, driver in enumerate(drivers):
        try:
            stints = get_stint_summary(session, driver)
        except Exception as e:
            print(f"Skipping {driver}: {e}")
            continue

        for _, row in stints.iterrows():
            compound = row["Compound"]
            color = COMPOUND_COLORS.get(compound, COMPOUND_COLORS["UNKNOWN"])
            ax.barh(
                driver,
                row["NumLaps"],
                left=row["StartLap"],
                color=color,
                edgecolor="black",
                height=0.6,
            )
            if row["NumLaps"] > 3:
                ax.text(
                    row["StartLap"] + row["NumLaps"] / 2,
                    i,
                    compound[:1],  # S / M / H / I / W
                    ha="center",
                    va="center",
                    fontsize=8,
                    fontweight="bold",
                    color="black",
                )

    # Legend
    legend_patches = [
        mpatches.Patch(color=color, label=compound, edgecolor="black")
        for compound, color in COMPOUND_COLORS.items()
        if compound != "UNKNOWN"
    ]
    ax.legend(handles=legend_patches, loc="lower right", fontsize=8)

    ax.set_xlabel("Lap Number")
    ax.set_title(title or "Tyre Strategy Comparison")
    plt.tight_layout()
    return fig


def compare_pace(session, drivers: list[str]):
    """
    Line chart comparing lap times across drivers for pace analysis.
    """
    fig, ax = plt.subplots(figsize=(12, 5))

    for driver in drivers:
        try:
            laps = get_driver_laps(session, driver)
            ax.plot(laps["LapNumber"], laps["LapTimeSeconds"], label=driver, linewidth=1.5)
        except Exception as e:
            print(f"Skipping {driver}: {e}")

    ax.set_xlabel("Lap Number")
    ax.set_ylabel("Lap Time (s)")
    ax.set_title("Lap Time Comparison")
    ax.legend()
    plt.tight_layout()
    return fig


if __name__ == "__main__":
    session = load_session(2023, "Monaco")
    drivers = ["VER", "HAM", "ALO"]

    fig1 = plot_strategy_comparison(session, drivers, title="Tyre Strategy – Monaco 2023")
    fig2 = compare_pace(session, drivers)
    plt.show()