import math
import random

import pygame

from constants import PALETTE_CLAY, PALETTE_LEATHER, PALETTE_TORCH

# Presets: one recipe per effect. Ranges are (lowest, highest), picked at random per particle
CRATE_DEBRIS = {
    "count": 8,
    "colors": (PALETTE_LEATHER, PALETTE_TORCH, PALETTE_CLAY),
    "speed": (40, 100),  # pixels per second
    "lifetime": (0.25, 0.45),  # seconds
    "size": (2, 3),  # pixels, square
    "drag": 6,  # how fast they slow down; higher stops sooner
}


def emit_burst(particles, center, preset):
    for _ in range(preset["count"]):
        speed = random.uniform(*preset["speed"])
        direction = random.uniform(0, 360)

        particles.append(
            {
                "pos": pygame.Vector2(center),
                "velocity": pygame.Vector2(speed, 0).rotate(direction),
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
