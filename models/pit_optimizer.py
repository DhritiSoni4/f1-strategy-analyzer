import numpy as np

def compute_total_time(pit_lap, total_laps, deg_rate, gap_behind, pit_loss=20):
    # Before pit
    laps_before = pit_lap
    loss_before = deg_rate * (laps_before * (laps_before + 1) / 2)

    # After pit
    laps_after = total_laps - pit_lap
    loss_after = deg_rate * (laps_after * (laps_after + 1) / 2)

    # Traffic penalty
    traffic_penalty = 0
    if gap_behind < pit_loss:
        traffic_penalty = 5  # simple constant penalty

    return loss_before + pit_loss + loss_after + traffic_penalty


def find_optimal_pit(total_laps, deg_rate, gap_behind):
    results = []

    for lap in range(1, total_laps):
        total_time = compute_total_time(
            lap, total_laps, deg_rate, gap_behind
        )
        results.append((lap, total_time))

    optimal_lap, min_time = min(results, key=lambda x: x[1])

    return {
        "optimal_pit_lap": optimal_lap,
        "min_time_loss": min_time
    }