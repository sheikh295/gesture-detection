"""Fire / power-fist particle effect."""

import random
import math
import numpy as np
import cv2
from .base_effect import BaseEffect
from utils import landmark_to_pixel
from config import PARTICLE_COUNT


class Particle:
    def __init__(self, x: int, y: int):
        self.x = float(x)
        self.y = float(y)
        angle = random.uniform(-math.pi / 2 - 0.6, -math.pi / 2 + 0.6)
        speed = random.uniform(2, 7)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 1.0
        self.decay = random.uniform(0.04, 0.08)
        self.radius = random.randint(4, 10)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy -= 0.15  # slight upward acceleration
        self.life -= self.decay
        self.radius = max(1, self.radius - 0.2)

    @property
    def alive(self):
        return self.life > 0


class FireEffect(BaseEffect):
    def __init__(self):
        super().__init__()
        self._particles: list[Particle] = []
        self._center = (320, 240)

    def update(self, frame, hand_landmarks_list, gesture):
        self.tick()
        if hand_landmarks_list:
            lm = hand_landmarks_list[0].landmark
            self._center = landmark_to_pixel(lm[0], frame.shape)  # wrist

        # Emit new particles
        cx, cy = self._center
        for _ in range(PARTICLE_COUNT):
            self._particles.append(
                Particle(cx + random.randint(-20, 20), cy + random.randint(-10, 10))
            )

        # Update existing
        self._particles = [p for p in self._particles if p.alive]
        for p in self._particles:
            p.update()

    def draw(self, frame):
        overlay = np.zeros_like(frame, dtype=np.uint8)
        for p in self._particles:
            t = 1.0 - p.life  # 0 = new, 1 = old
            # red → orange → yellow gradient
            r = 255
            g = int(min(255, t * 510))
            b = 0
            color = (b, g, r)
            cv2.circle(overlay, (int(p.x), int(p.y)), int(p.radius), color, -1)

        cv2.addWeighted(frame, 1.0, overlay, 0.85, 0, frame)

    def reset(self):
        super().reset()
        self._particles.clear()
