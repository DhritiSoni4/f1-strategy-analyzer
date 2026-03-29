def simulate_undercut(
    deg_rate,
    laps_delta=3,
    tire_advantage=1.5
):
    """
    laps_delta: how many laps earlier you pit than rival
    tire_advantage: seconds gained per lap on fresh tires
    """

    # Time gained from fresh tires
    gain = laps_delta * tire_advantage

    # Time lost due to staying out longer (degradation)
    loss = deg_rate * (laps_delta * (laps_delta + 1) / 2)

    net_gain = gain - loss

    return {
        "undercut_gain": net_gain
    }


def simulate_overcut(
    deg_rate,
    laps_delta=3,
    tire_advantage=1.5
):
    """
    Opposite of undercut
    """

    # You stay out → lose due to degradation
    loss = deg_rate * (laps_delta * (laps_delta + 1) / 2)

    # Rival gets fresh tires → they gain
    rival_gain = laps_delta * tire_advantage

    net_gain = -loss - rival_gain

    return {
        "overcut_gain": net_gain
    }