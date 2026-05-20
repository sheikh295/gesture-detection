"""Kamehameha — electric blue energy beam firing from cupped hands."""

import math
import random
import numpy as np
import cv2
from .base_effect import BaseEffect
from utils import hand_center, landmark_to_pixel
from config import PARTICLE_COUNT


class KamehamehaEffect(BaseEffect):
    def __init__(self):
        super().__init__()
        self._origin = (320, 360)
        self._charge = 0      # 0–60 charging frames
        self._particles = []  # swirling charge particles

    def update(self, frame, hand_landmarks_list, gesture):
        self.tick()
        h, w = frame.shape[:2]

        if hand_landmarks_list:
            # Use centroid of all detected hands as beam origin
            centers = [hand_center(hl, frame.shape) for hl in hand_landmarks_list]
            self._origin = (
                int(sum(c[0] for c in centers) / len(centers)),
                int(sum(c[1] for c in centers) / len(centers)),
            )

        # Charge grows up to 60 frames
        self._charge = min(60, self._charge + 1)

        # Emit swirling charge particles
        ox, oy = self._origin
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(30, 80)
            px = ox + math.cos(angle) * dist
            py = oy + math.sin(angle) * dist
            vx = (ox - px) * 0.15
            vy = (oy - py) * 0.15
            self._particles.append([px, py, vx, vy, 1.0])

        # Update particles
        alive = []
        for p in self._particles:
            p[0] += p[2]
            p[1] += p[3]
            p[4] -= 0.05
            if p[4] > 0:
                alive.append(p)
        self._particles = alive

    def draw(self, frame):
        h, w = frame.shape[:2]
        ox, oy = self._origin
        t = self._charge / 60.0  # 0 → 1 over charge time

        # Draw swirling charge particles
        for p in self._particles:
            alpha = p[4]
            color = (int(255 * alpha), int(100 * alpha), int(20 * alpha))
            cv2.circle(frame, (int(p[0]), int(p[1])), 3, color, -1)

        if t < 0.3:
            return  # still charging, no beam yet

        # Beam: starts narrow at hands, expands to right edge
        beam_w_near = int(10 * t)
        beam_w_far = int(50 * t)
        beam_x_far = w

        pts_top = [(ox, oy - beam_w_near), (beam_x_far, oy - beam_w_far)]
        pts_bot = [(ox, oy + beam_w_near), (beam_x_far, oy + beam_w_far)]
        poly = np.array([pts_top[0], pts_top[1], pts_bot[1], pts_bot[0]], dtype=np.int32)

        # Glow layers
        for width_extra, color, alpha in [
            (20, (180, 30, 0), 0.2),
            (10, (255, 80, 0), 0.35),
            (4, (255, 200, 50), 0.5),
        ]:
            glow_pts = np.array([
                (ox, oy - beam_w_near - width_extra),
                (beam_x_far, oy - beam_w_far - width_extra),
                (beam_x_far, oy + beam_w_far + width_extra),
                (ox, oy + beam_w_near + width_extra),
            ], dtype=np.int32)
            glow = frame.copy()
            cv2.fillPoly(glow, [glow_pts], color)
            cv2.addWeighted(glow, alpha, frame, 1 - alpha, 0, frame)

        # Core beam fill
        beam_overlay = frame.copy()
        cv2.fillPoly(beam_overlay, [poly], (255, 200, 20))
        cv2.addWeighted(beam_overlay, 0.7, frame, 0.3, 0, frame)

        # Animated wave lines inside beam
        wave_offset = int(math.sin(self._frame_count * 0.4) * 6)
        for i in range(3):
            wave_y = oy - beam_w_near // 3 + i * (beam_w_near // 3 * 2) + wave_offset
            cv2.line(frame, (ox, wave_y), (beam_x_far, wave_y), (255, 255, 255), 1)

        # Bright core center line
        cv2.line(frame, (ox, oy), (beam_x_far, oy), (255, 255, 255), 2)

    def reset(self):
        super().reset()
        self._charge = 0
        self._particles.clear()
