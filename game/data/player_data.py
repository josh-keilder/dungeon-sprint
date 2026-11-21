# The player's values, read once by Player.__init__ (like ENEMY_TYPES for enemies).
# Every key is required; Player reads them with player_data["..."].
PLAYER_DATA = {
    # Before equipment bonuses; compute_stats adds each equipped item's bonuses
    "base_stats": {
        "defense": 0,
        "health": 25,
        "roll_speed": 200,  # pixels per second at the start of a roll
        "max_speed": 70,  # pixels per second, walking
        "acceleration_rate": 20,
        "deceleration_rate": 60,
        "grip": 50,
    },
    # Being hit
    "invulnerability_duration": 1.0,  # seconds of i-frames after a hit
    "blink_interval": 0.1,  # seconds per blink on/off while invulnerable
    "knockback_speed": 160,  # pixels per second, away from the enemy that hit
    "knockback_decay_rate": 16,  # how fast the push slows; distance = speed / decay
    # Inventory
    "inventory_slot_count": 20,
    # In the order the inventory screen draws them
    "equipment_slot_names": ("head", "chest", "boots", "ability"),
}
