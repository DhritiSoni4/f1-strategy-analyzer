import streamlit as st
import fastf1
import fastf1.plotting
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

fastf1.plotting.setup_mpl()

st.title("🏎️ F1 Strategy Analyzer")

# Dropdowns
year = st.selectbox("Select Year", [2022, 2023])

race = st.selectbox(
    "Select Race",
    ["Bahrain", "Saudi Arabia", "Australia", "Monaco", "Silverstone", "Spa"]
)

@st.cache_data
def load_session(year, race):
    session = fastf1.get_session(year, race, "R")
    session.load()
    return session

session = load_session(year, race)

drivers = session.drivers
driver = st.selectbox("Select Driver", drivers)

if st.button("Run Analysis"):

    laps = session.laps.pick_drivers(driver)

    laps = laps[["LapNumber", "LapTime", "Compound"]].dropna()
    laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()

    laps = laps[laps["LapTimeSeconds"] < laps["LapTimeSeconds"].quantile(0.95)]

    original_time = laps["LapTimeSeconds"].sum()

    compound_deg = {
        "SOFT": 0.05,
        "MEDIUM": 0.03,
        "HARD": 0.02,
        "INTERMEDIATE": 0.025,
        "WET": 0.03
    }

    def simulate_stint(lap_times, compounds, after_pit=False):
        total = 0
        for i, (lap, comp) in enumerate(zip(lap_times, compounds)):
            base_deg = compound_deg.get(comp, 0.03)
            degradation = base_deg * (i ** 1.2)

            if after_pit:
                lap_time = lap * 0.97 + degradation
            else:
                lap_time = lap + degradation

            total += lap_time

        return total

    results = []

    for pit_lap in range(10, int(laps["LapNumber"].max()) - 5):

        stint1 = laps[laps["LapNumber"] <= pit_lap]
        stint2 = laps[laps["LapNumber"] > pit_lap]

        t1 = simulate_stint(
            stint1["LapTimeSeconds"].values,
            stint1["Compound"].values
        )

        t2 = simulate_stint(
            stint2["LapTimeSeconds"].values,
            stint2["Compound"].values,
            after_pit=True
        )

        total_time = t1 + t2
        results.append((pit_lap, total_time))

    results_df = pd.DataFrame(results, columns=["PitLap", "TotalTime"])

    best_row = results_df.loc[results_df["TotalTime"].idxmin()]
    best_lap = int(best_row["PitLap"])
    best_time = best_row["TotalTime"]

    gain = original_time - best_time

    st.subheader("📊 Results")
    st.write(f"Optimal Pit Lap: {best_lap}")
    st.write(f"Time Gain: {round(gain,2)} seconds")

    fig, ax = plt.subplots()
    ax.plot(results_df["PitLap"], results_df["TotalTime"])
    ax.scatter(best_lap, best_time)
    ax.axvline(best_lap, linestyle="--")

    ax.set_xlabel("Pit Lap")
    ax.set_ylabel("Total Time")
    ax.set_title("Strategy Optimization Curve")

    st.pyplot(fig)