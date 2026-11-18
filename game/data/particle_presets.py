from game.data.palette import (
    PALETTE_AZURE,
    PALETTE_BONE,
    PALETTE_CLAY,
    PALETTE_FROST,
    PALETTE_ICE,
    PALETTE_LEATHER,
    PALETTE_OAK,
    PALETTE_TAN,
    PALETTE_TORCH,
)

# Particle looks, handed to emit_burst by the floor and ENEMY_TYPES

# Crates breaking: all around the crate
CRATE_DEBRIS = {
    "count": 8,
    "colors": (PALETTE_LEATHER, PALETTE_TORCH, PALETTE_CLAY),
    "speed": (40, 100),  # pixels per second
    "lifetime": (0.25, 0.45),  # seconds
    "size": (2, 3),  # pixels, square
    "drag": 6,  # how fast they slow down; higher stops sooner
    "spread": 360,  # degrees around the direction; 360 = all around
}

# Roll hits: sprayed away from the player, along the knockback
BONE_CHIPS = {
    "count": 6,
    "colors": (PALETTE_BONE, PALETTE_TAN, PALETTE_OAK),
    "speed": (50, 110),
    "lifetime": (0.2, 0.4),
    "size": (1, 2),
    "drag": 7,
    "spread": 120,
}

SKULL_SPARKS = {
    "count": 7,
    "colors": (PALETTE_AZURE, PALETTE_FROST, PALETTE_ICE),
    "speed": (60, 130),
    "lifetime": (0.15, 0.3),
    "size": (1, 2),
    "drag": 8,
    "spread": 140,
}
