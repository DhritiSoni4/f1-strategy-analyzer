import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt

# Enable FastF1 plotting style
fastf1.plotting.setup_mpl()

# Load race session
session = fastf1.get_session(2023, "Monaco", "R")
session.load()

# Select driver
driver = "VER"

# Get laps for the driver
laps = session.laps.pick_drivers(driver)

# Extract stint information
stints = laps[["Stint", "Compound", "LapNumber"]]
stints = stints.groupby(["Stint", "Compound"]).count().reset_index()

# Print tyre strategy in terminal
print("\nTyre Stints:")
for _, row in stints.iterrows():
    print(f"{row['Compound']} for {row['LapNumber']} laps")

# Tyre colors
compound_colors = {
    "SOFT": "red",
    "MEDIUM": "yellow",
    "HARD": "white",
    "INTERMEDIATE": "green",
    "WET": "blue"
}

# Plot
fig, ax = plt.subplots(figsize=(10, 2))

previous = 0

for _, row in stints.iterrows():
    compound = row["Compound"]
    stint_laps = row["LapNumber"]

    ax.barh(
        driver,
        stint_laps,
        left=previous,
        color=compound_colors.get(compound, "grey"),
        edgecolor="black"
    )

    # Label compound
    ax.text(
        previous + stint_laps / 2,
        0,
        compound,
        ha="center",
        va="center",
        fontsize=10
    )

    # Label lap start
    ax.text(
        previous,
        -0.15,
        f"Lap {previous}",
        fontsize=8
    )

    previous += stint_laps

ax.set_title(f"{driver} Tyre Strategy – Monaco 2023")
ax.set_xlabel("Lap Number")
ax.set_yticks([])

plt.tight_layout()
plt.show()