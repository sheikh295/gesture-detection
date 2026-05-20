"""Spirit Bomb — glowing blue energy sphere above the open palm."""

import math
import numpy as np
import cv2
from .base_effect import BaseEffect
from utils import landmark_to_pixel


class SpiritBombEffect(BaseEffect):
    def __init__(self):
        super().__init__()
        self._center = (320, 120)
        self._max_radius = 90
        self._radius = 10
        self._angle = 0.0

    def update(self, frame, hand_landmarks_list, gesture):
        self.tick()
        if hand_landmarks_list:
            lm = hand_landmarks_list[0].landmark
            wrist = landmark_to_pixel(lm[0], frame.shape)
            # Position sphere above wrist
            self._center = (wrist[0], max(60, wrist[1] - 130))

        # Grow radius over time
        if self._radius < self._max_radius:
            self._radius = min(self._max_radius, self._radius + 0.8)

        self._angle += 0.05

    def draw(self, frame):
        cx, cy = self._center
        r = int(self._radius)
        pulse = int(math.sin(self._frame_count * 0.15) * 6)
        r_pulse = r + pulse

        overlay = frame.copy()

        # Outer glow layers
        for i in range(5, 0, -1):
            alpha = 0.08 * i
            glow_r = r_pulse + i * 8
            cv2.circle(overlay, (cx, cy), glow_r, (255, 180, 20), -1)

        cv2.addWeighted(overlay, 0.25, frame, 0.75, 0, frame)

        # Core sphere
        cv2.circle(frame, (cx, cy), r_pulse, (255, 220, 60), -1)
        cv2.circle(frame, (cx, cy), r_pulse, (255, 255, 200), 2)

        # Inner bright spot
        cv2.circle(frame, (cx - r // 4, cy - r // 4), max(4, r // 4), (255, 255, 255), -1)

        # Rotating spokes
        num_spokes = 8
        for i in range(num_spokes):
            angle = self._angle + i * (2 * math.pi / num_spokes)
            x2 = int(cx + (r_pulse + 20) * math.cos(angle))
            y2 = int(cy + (r_pulse + 20) * math.sin(angle))
            cv2.line(frame, (cx, cy), (x2, y2), (200, 240, 255), 1)

        # Concentric rings
        for ring in range(1, 4):
            ring_r = r_pulse * ring // 3
            cv2.circle(frame, (cx, cy), ring_r, (200, 230, 255), 1)

    def reset(self):
        super().reset()
        self._radius = 10
