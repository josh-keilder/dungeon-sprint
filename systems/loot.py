import random


def roll_loot(loot_table):
    drops = []

    for entry in loot_table:
        if random.random() < entry["chance"]:
            quantity = random.randint(entry["min_quantity"], entry["max_quantity"])
            drops.append((entry["item_id"], quantity))

    return drops
