SPEED_RAMP_MAX = 30
SPEED_RAMP_GAIN = 240
SPEED_RAMP_DECAY = 1200


def compute_stats(base_stats, equipped_items):

    stats = base_stats.copy()

    for item in equipped_items:
        if item is None or not item.stats:
            continue

        for stat_name, bonus in item.stats.items():
            if stat_name in stats:
                stats[stat_name] += bonus

    return stats


def update_speed_ramp(ramp, building, dt):
    if building:
        return min(ramp + SPEED_RAMP_GAIN * dt, SPEED_RAMP_MAX)
    else:
        return max(ramp - SPEED_RAMP_DECAY * dt, 0)
