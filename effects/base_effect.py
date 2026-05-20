"""Abstract base class for all visual effects."""

from abc import ABC, abstractmethod
import numpy as np


class BaseEffect(ABC):
    def __init__(self):
        self._frame_count = 0

    @abstractmethod
    def update(self, frame: np.ndarray, hand_landmarks_list: list, gesture: str) -> None:
        """Update effect state for the current frame."""

    @abstractmethod
    def draw(self, frame: np.ndarray) -> None:
        """Draw effect onto frame in-place."""

    def reset(self) -> None:
        """Reset internal state (called when gesture changes away)."""
        self._frame_count = 0

    def tick(self) -> None:
        self._frame_count += 1
