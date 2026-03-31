import numpy as np

def tire_time_loss(lap_age, deg_rate):
    if lap_age <= 5:
        return deg_rate * lap_age * 0.5
    elif lap_age <= 15:
        return deg_rate * lap_age
    else:
        return deg_rate * lap_age + 0.2 * (lap_age - 15) ** 2
    
def compute_total_time(pit_lap, total_laps, deg_rate, gap_behind, pit_loss=20):
    
    # Before pit (degrading tire)
    laps_before = pit_lap
    loss_before = sum(
    tire_time_loss(lap, deg_rate) for lap in range(1, laps_before + 1)
)
    # After pit (fresh tire → slower degradation effect)
    laps_after = total_laps - pit_lap
    fresh_tire_gain = 5.0 
    
    # 🔥 KEY FIX: fresh tires are faster (reduce degradation effect)
    fresh_deg_rate = deg_rate * 0.6  # assume 40% better performance
    
    loss_after = sum(
    tire_time_loss(lap + 3, fresh_deg_rate) for lap in range(1, laps_after + 1))

    # Traffic penalt
    traffic_penalty = 0
    if gap_behind < pit_loss:
        traffic_penalty = 5

    return loss_before + pit_loss + loss_after + traffic_penalty - fresh_tire_gain

def find_optimal_pit(total_laps, deg_rate, gap_behind):
    results = []
    max_stint = min(total_laps, 20)

    for lap in range(1, max_stint):
        total_time = compute_total_time(
            lap, total_laps, deg_rate, gap_behind
        )
        results.append((lap, total_time))

    optimal_lap, min_time = min(results, key=lambda x: x[1])

    return {
        "optimal_pit_lap": optimal_lap,
        "min_time_loss": min_time
    }