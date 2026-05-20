"""Super Saiyan Aura — golden frame-wide lightning aura effect."""

import math
import random
import numpy as np
import cv2
from .base_effect import BaseEffect


class AuraEffect(BaseEffect):
    def __init__(self):
        super().__init__()
        self._bolts = []  # list of lightning bolt point lists
        self._bolt_timer = 0

    def _gen_bolt(self, frame_shape):
        """Generate a jagged lightning bolt along the frame border."""
        h, w = frame_shape[:2]
        side = random.choice(["left", "right", "top", "bottom"])
        if side == "left":
            sx, sy = 0, random.randint(0, h)
            ex, ey = random.randint(20, 120), random.randint(0, h)
        elif side == "right":
            sx, sy = w, random.randint(0, h)
            ex, ey = w - random.randint(20, 120), random.randint(0, h)
        elif side == "top":
            sx, sy = random.randint(0, w), 0
            ex, ey = random.randint(0, w), random.randint(20, 120)
        else:
            sx, sy = random.randint(0, w), h
            ex, ey = random.randint(0, w), h - random.randint(20, 120)

        pts = [(sx, sy)]
        steps = random.randint(5, 10)
        for i in range(1, steps):
            t = i / steps
            px = int(sx + (ex - sx) * t + random.randint(-20, 20))
            py = int(sy + (ey - sy) * t + random.randint(-20, 20))
            pts.append((px, py))
        pts.append((ex, ey))
        return pts

    def update(self, frame, hand_landmarks_list, gesture):
        self.tick()
        self._bolt_timer += 1
        if self._bolt_timer >= 3:
            self._bolt_timer = 0
            # Add 2-4 new bolts
            for _ in range(random.randint(2, 4)):
                self._bolts.append({
                    "pts": self._gen_bolt(frame.shape),
                    "life": random.randint(3, 8),
                })

        # Age bolts
        alive = []
        for b in self._bolts:
            b["life"] -= 1
            if b["life"] > 0:
                alive.append(b)
        self._bolts = alive

    def draw(self, frame):
        h, w = frame.shape[:2]

        # Subtle golden tint overlay (~15% opacity)
        tint = np.zeros_like(frame, dtype=np.uint8)
        tint[:] = (0, 160, 255)  # gold in BGR
        cv2.addWeighted(tint, 0.12, frame, 0.88, 0, frame)

        # Draw each lightning bolt
        for b in self._bolts:
            pts = b["pts"]
            life_ratio = b["life"] / 8.0
            # Glow pass
            for i in range(len(pts) - 1):
                glow = frame.copy()
                cv2.line(glow, pts[i], pts[i + 1], (0, 200, 255), 6)
                cv2.addWeighted(glow, 0.3 * life_ratio, frame, 1 - 0.3 * life_ratio, 0, frame)
            # Core bolt
            for i in range(len(pts) - 1):
                cv2.line(frame, pts[i], pts[i + 1], (0, 240, 255), 2)

    def reset(self):
        super().reset()
        self._bolts.clear()
        self._bolt_timer = 0
