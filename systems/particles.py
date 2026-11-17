import math
import random

import pygame

from constants import (
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

# Presets: one recipe per effect. Ranges are (lowest, highest), picked at random per particle
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


def emit_burst(particles, center, preset, direction=None):
    # Particles fly within `spread` degrees around the direction (any way if none)
    base_angle = 0
    if direction is not None and direction.length_squared() > 0:
        base_angle = direction.as_polar()[1]
    half_spread = preset["spread"] / 2

    for _ in range(preset["count"]):
        speed = random.uniform(*preset["speed"])
        angle = base_angle + random.uniform(-half_spread, half_spread)

        particles.append(
            {
                "pos": pygame.Vector2(center),
                "velocity": pygame.Vector2(speed, 0).rotate(angle),
                "color": random.choice(preset["colors"]),
                "size": random.randint(*preset["size"]),
                "drag": preset["drag"],
                "lifetime": random.uniform(*preset["lifetime"]),
                "age": 0.0,
            }
        )


def update_particles(particles, dt):
    for particle in particles:
        particle["age"] += dt
        particle["pos"] += particle["velocity"] * dt
        particle["velocity"] *= math.exp(-particle["drag"] * dt)

    particles[:] = [
        particle for particle in particles if particle["age"] < particle["lifetime"]
    ]


def draw_particles(surface, particles, camera):
    for particle in particles:
        life_left = 1 - particle["age"] / particle["lifetime"]
        size = max(1, math.ceil(particle["size"] * life_left))

        x = int(particle["pos"].x - camera.x)
        y = int(particle["pos"].y - camera.y)
        surface.fill(particle["color"], (x, y, size, size))
