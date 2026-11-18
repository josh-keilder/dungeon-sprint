import math
import random

import pygame

from engine.graphics.camera import world_to_screen

# A preset is one recipe per effect, made by the game. Ranges are (lowest, highest),
# picked at random per particle:
#   "count":    particles per burst
#   "colors":   a tuple of colors, one picked per particle
#   "speed":    (low, high) pixels per second
#   "lifetime": (low, high) seconds
#   "size":     (low, high) pixels, square
#   "drag":     how fast they slow down; higher stops sooner
#   "spread":   degrees around the direction; 360 = all around


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

        x, y = world_to_screen(camera, particle["pos"])
        surface.fill(particle["color"], (int(x), int(y), size, size))
