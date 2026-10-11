def compute_stats(base_stats, equipped_items):

    stats = base_stats.copy()

    for item in equipped_items:
        if item is None or not item.stats:
            continue

        for stat_name, bonus in item.stats.items():
            if stat_name in stats:
                stats[stat_name] += bonus

    return stats
