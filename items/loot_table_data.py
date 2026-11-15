# Loot tables: each entry is rolled on its own, so one roll can drop several things.
# "chance" is 0.0 to 1.0; the quantity is a random whole number from min to max.

# Containers
CHEST_LOOT = [
    {
        "item_id": "small_health_potion",
        "chance": 0.5,
        "min_quantity": 1,
        "max_quantity": 3,
    },
    {"item_id": "speed_boots", "chance": 0.08, "min_quantity": 1, "max_quantity": 1},
]

CRATE_LOOT = [
    {
        "item_id": "small_health_potion",
        "chance": 0.15,
        "min_quantity": 1,
        "max_quantity": 2,
    },
]

# Enemies (attached to each type as "loot_table" in ENEMY_TYPES)
SKULL_LOOT = [
    {
        "item_id": "small_health_potion",
        "chance": 0.25,
        "min_quantity": 1,
        "max_quantity": 1,
    },
]

SKELETON_LOOT = [
    {
        "item_id": "small_health_potion",
        "chance": 0.35,
        "min_quantity": 1,
        "max_quantity": 1,
    },
]
