"""Effects package — exports all effect classes and the EffectManager."""

from .base_effect import BaseEffect
from .fire import FireEffect
from .spirit_bomb import SpiritBombEffect
from .sword import SwordEffect
from .shield import ShieldEffect
from .kamehameha import KamehamehaEffect
from .aura import AuraEffect


class EffectManager:
    """
    Manages the active visual effect, handles gesture transitions,
    and provides smooth fade-out between effects.
    """

    _GESTURE_TO_EFFECT = {
        "FIST":      FireEffect,
        "OPEN_PALM": SpiritBombEffect,
        "POINTING":  SwordEffect,
        "PEACE":     ShieldEffect,
        "PINCH":     KamehamehaEffect,
        "HORNS":     AuraEffect,
    }

    def __init__(self, fade_frames: int = 10):
        self._active_effect: BaseEffect | None = None
        self._prev_effect: BaseEffect | None = None
        self._current_gesture: str = "NONE"
        self._fade_frames = fade_frames
        self._fade_counter: int = 0

    def update(self, gesture: str, frame, hand_landmarks_list: list) -> None:
        if gesture != self._current_gesture:
            # Start fade-out of old effect
            self._prev_effect = self._active_effect
            self._fade_counter = self._fade_frames

            # Instantiate new effect (or None for "NONE")
            cls = self._GESTURE_TO_EFFECT.get(gesture)
            if cls:
                self._active_effect = cls()
            else:
                self._active_effect = None
            self._current_gesture = gesture

        # Tick fade counter
        if self._fade_counter > 0:
            self._fade_counter -= 1
            if self._fade_counter == 0:
                if self._prev_effect:
                    self._prev_effect.reset()
                self._prev_effect = None

        # Update active effect
        if self._active_effect:
            self._active_effect.update(frame, hand_landmarks_list, gesture)

    def draw(self, frame) -> None:
        import cv2
        import numpy as np

        # Draw fading-out previous effect
        if self._prev_effect and self._fade_counter > 0:
            temp = frame.copy()
            self._prev_effect.draw(temp)
            alpha = self._fade_counter / self._fade_frames
            cv2.addWeighted(temp, alpha, frame, 1 - alpha, 0, frame)

        # Draw active effect
        if self._active_effect:
            self._active_effect.draw(frame)


__all__ = [
    "BaseEffect",
    "FireEffect",
    "SpiritBombEffect",
    "SwordEffect",
    "ShieldEffect",
    "KamehamehaEffect",
    "AuraEffect",
    "EffectManager",
]
