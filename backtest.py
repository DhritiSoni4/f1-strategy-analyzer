import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st
import matplotlib.pyplot as plt

from data_loader import load_session, get_driver_laps
from pit_optimizer import optimize_pit_window, get_best_pit_lap, plot_pit_window
from strategy_comparator import plot_strategy_comparison, compare_pace
from tire_model import load_params

st.set_page_config(page_title="F1 Strategy Analyzer", page_icon="🏎️", layout="wide")
st.title("🏎️ F1 Strategy Analyzer")

# ── Sidebar controls ──────────────────────────────────────────────────────────
st.sidebar.header("Race Settings")

year = st.sidebar.selectbox("Year", [2022, 2023, 2024])

RACES = {
    "Bahrain":    "bahrain",
    "Australia":  "default",
    "Monaco":     "monaco",
    "Silverstone":"silverstone",
    "Monza":      "monza",
    "Abu Dhabi":  "default",
}
race_name = st.sidebar.selectbox("Race", list(RACES.keys()))
circuit_key = RACES[race_name]

compound_after_pit = st.sidebar.selectbox(
    "Compound after pit", ["MEDIUM", "HARD", "SOFT"]
)

# ── Session loading ───────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading session data...")
def cached_session(year, race):
    return load_session(year, race)

session = cached_session(year, race_name)
all_drivers = list(session.drivers)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Pit Optimizer", "Strategy Comparison", "Pace Analysis"])

# ── Tab 1: Pit Optimizer ──────────────────────────────────────────────────────
with tab1:
    st.subheader("One-Stop Pit Window Optimizer")
    driver = st.selectbox("Driver", all_drivers, key="opt_driver")

    if st.button("Run Optimizer"):
        with st.spinner("Optimizing..."):
            params = load_params()
            try:
                results_df = optimize_pit_window(
                    session, driver, circuit_key,
                    compound_after_pit=compound_after_pit,
                    params=params,
                )
                best = get_best_pit_lap(results_df)

                col1, col2 = st.columns(2)
                col1.metric("Optimal Pit Lap", f"Lap {best['pit_lap']}")
                col2.metric("Predicted Total Time", f"{best['total_time']} s")

                fig = plot_pit_window(results_df, driver, f"{race_name} {year}")
                st.pyplot(fig)
                plt.close()

                with st.expander("Full results table"):
                    st.dataframe(results_df, use_container_width=True)

            except Exception as e:
                st.error(f"Error: {e}")

# ── Tab 2: Strategy Comparison ────────────────────────────────────────────────
with tab2:
    st.subheader("Tyre Strategy Comparison")
    selected_drivers = st.multiselect(
        "Select drivers to compare", all_drivers,
        default=all_drivers[:3] if len(all_drivers) >= 3 else all_drivers,
    )

    if st.button("Plot Strategy") and selected_drivers:
        with st.spinner("Building strategy chart..."):
            try:
                fig = plot_strategy_comparison(
                    session, selected_drivers,
                    title=f"Tyre Strategy – {race_name} {year}"
                )
                st.pyplot(fig)
                plt.close()
            except Exception as e:
                st.error(f"Error: {e}")

# ── Tab 3: Pace Analysis ──────────────────────────────────────────────────────
with tab3:
    st.subheader("Lap Time Pace Comparison")
    pace_drivers = st.multiselect(
        "Select drivers", all_drivers,
        default=all_drivers[:3] if len(all_drivers) >= 3 else all_drivers,
        key="pace_drivers",
    )

    if st.button("Plot Pace") and pace_drivers:
        with st.spinner("Loading lap times..."):
            try:
                fig = compare_pace(session, pace_drivers)
                st.pyplot(fig)
                plt.close()
            except Exception as e:
                st.error(f"Error: {e}")