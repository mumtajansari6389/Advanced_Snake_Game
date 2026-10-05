import random
import pygame
from settings import BLOCK

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit_food_particles(self, pos, color, count=12):
        for _ in range(count):
            self.particles.append({
                "x": pos[0] * BLOCK + BLOCK // 2,
                "y": pos[1] * BLOCK + BLOCK // 2,
                "vx": random.uniform(-3, 3),
                "vy": random.uniform(-3, 3),
                "life": 25,
                "color": random.choice([color, (255, 255, 255)]),
            })

    def update(self):
        self.particles = [p for p in self.particles if p["life"] > 0]
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1

    def draw(self, surface):
        for p in self.particles:
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), 2)

