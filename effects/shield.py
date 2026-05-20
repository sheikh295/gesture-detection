"""Ki Shield — translucent rotating aura shield around the hand."""

import math
import numpy as np
import cv2
from .base_effect import BaseEffect
from utils import hand_center
from config import SHIELD_RADIUS


class ShieldEffect(BaseEffect):
    def __init__(self):
        super().__init__()
        self._center = (320, 240)
        self._angle = 0.0

    def update(self, frame, hand_landmarks_list, gesture):
        self.tick()
        if hand_landmarks_list:
            self._center = hand_center(hand_landmarks_list[0], frame.shape)
        self._angle += 0.06

    def draw(self, frame):
        cx, cy = self._center
        pulse = int(math.sin(self._frame_count * 0.12) * 10)
        r = SHIELD_RADIUS + pulse

        overlay = frame.copy()

        # Semi-transparent fill
        cv2.ellipse(overlay, (cx, cy), (r, int(r * 0.7)), 0, 0, 360, (0, 255, 136), -1)
        cv2.addWeighted(overlay, 0.18, frame, 0.82, 0, frame)

        # Outer glow rings
        for i in range(3):
            glow = frame.copy()
            cv2.ellipse(glow, (cx, cy), (r + i * 5, int((r + i * 5) * 0.7)), 0, 0, 360,
                        (0, 255, 136), 2)
            cv2.addWeighted(glow, 0.25, frame, 0.75, 0, frame)

        # Rotating arc dashes
        num_dashes = 12
        dash_arc = 15  # degrees
        for i in range(num_dashes):
            start_angle = int(math.degrees(self._angle) + i * (360 / num_dashes))
            end_angle = start_angle + dash_arc
            cv2.ellipse(frame, (cx, cy), (r, int(r * 0.7)), 0, start_angle, end_angle,
                        (150, 255, 200), 3)

        # Bright border
        cv2.ellipse(frame, (cx, cy), (r, int(r * 0.7)), 0, 0, 360, (0, 255, 100), 2)

    def reset(self):
        super().reset()
        self._angle = 0.0
