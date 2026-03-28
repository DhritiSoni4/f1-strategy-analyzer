import numpy as np

def compute_total_time(pit_lap, total_laps, deg_rate, pit_loss=20):
    """
    pit_lap: lap to pit on (1-indexed within remaining laps)
    total_laps: total laps remaining
    deg_rate: tire degradation per lap
    pit_loss: fixed time lost during pit stop (seconds)
    """

    # Before pit: degradation accumulates
    laps_before = pit_lap
    loss_before = deg_rate * (laps_before * (laps_before + 1) / 2)

    # After pit: reset degradation
    laps_after = total_laps - pit_lap
    loss_after = deg_rate * (laps_after * (laps_after + 1) / 2)

    return loss_before + pit_loss + loss_after


def find_optimal_pit(total_laps, deg_rate):
    results = []

    for lap in range(1, total_laps):
        total_time = compute_total_time(lap, total_laps, deg_rate)
        results.append((lap, total_time))

    optimal_lap, min_time = min(results, key=lambda x: x[1])

    return {
        "optimal_pit_lap": optimal_lap,
        "min_time_loss": min_time
    }