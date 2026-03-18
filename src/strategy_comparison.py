import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt

fastf1.plotting.setup_mpl()

session = fastf1.get_session(2023, "Monaco", "R")
session.load()

drivers = ["VER", "HAM", "ALO"]

compound_colors = {
    "SOFT": "red",
    "MEDIUM": "yellow",
    "HARD": "white",
    "INTERMEDIATE": "green",
    "WET": "blue"
}

fig, ax = plt.subplots(figsize=(10, 4))

for i, driver in enumerate(drivers):
    laps = session.laps.pick_drivers(driver)

    stints = laps[["Stint", "Compound", "LapNumber"]]
    stints = stints.groupby(["Stint", "Compound"]).count().reset_index()

    previous = 0

    print(f"\n{driver} Strategy:")

    for _, row in stints.iterrows():
        compound = row["Compound"]
        stint_laps = row["LapNumber"]

        print(f"{compound} for {stint_laps} laps")

        ax.barh(
            driver,
            stint_laps,
            left=previous,
            color=compound_colors.get(compound, "grey"),
            edgecolor="black"
        )

        # label inside bar
        ax.text(
            previous + stint_laps / 2,
            i,
            compound,
            ha="center",
            va="center",
            fontsize=9
        )

        previous += stint_laps

ax.set_title("Tyre Strategy Comparison – Monaco 2023")
ax.set_xlabel("Lap Number")

plt.tight_layout()
plt.show()