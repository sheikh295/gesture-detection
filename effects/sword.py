"""Energy Sword — glowing cyan blade extending from index fingertip."""

import math
import numpy as np
import cv2
from .base_effect import BaseEffect
from utils import landmark_to_pixel
from config import SWORD_LENGTH


class SwordEffect(BaseEffect):
    def __init__(self):
        super().__init__()
        self._tip = (320, 200)
        self._direction = (0.0, -1.0)  # pointing up by default

    def update(self, frame, hand_landmarks_list, gesture):
        self.tick()
        if not hand_landmarks_list:
            return
        lm = hand_landmarks_list[0].landmark
        wrist = landmark_to_pixel(lm[0], frame.shape)
        index_tip = landmark_to_pixel(lm[8], frame.shape)

        # Direction vector from wrist to fingertip
        dx = index_tip[0] - wrist[0]
        dy = index_tip[1] - wrist[1]
        length = math.sqrt(dx ** 2 + dy ** 2) or 1
        self._direction = (dx / length, dy / length)
        self._tip = index_tip

    def draw(self, frame):
        tip = self._tip
        dx, dy = self._direction
        shimmer = int(math.sin(self._frame_count * 0.3) * 8)
        blade_len = SWORD_LENGTH + shimmer

        blade_end = (
            int(tip[0] + dx * blade_len),
            int(tip[1] + dy * blade_len),
        )

        # Outer glow passes
        for width, color, alpha in [
            (14, (180, 60, 0), 0.3),
            (9, (255, 140, 0), 0.5),
            (5, (255, 220, 50), 0.8),
        ]:
            glow = frame.copy()
            cv2.line(glow, tip, blade_end, color, width)
            cv2.addWeighted(glow, alpha, frame, 1 - alpha, 0, frame)

        # Core bright line
        cv2.line(frame, tip, blade_end, (255, 255, 255), 2)

        # Handle (small yellow knob at fingertip)
        cv2.circle(frame, tip, 6, (0, 200, 255), -1)

    def reset(self):
        super().reset()
