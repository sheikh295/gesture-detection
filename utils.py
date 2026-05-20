"""Utility helpers for drawing, blending, and color operations."""

import cv2
import numpy as np


def alpha_blend(frame: np.ndarray, overlay: np.ndarray, alpha: float) -> np.ndarray:
    """Blend overlay onto frame with given alpha (0–1)."""
    return cv2.addWeighted(frame, 1.0, overlay, alpha, 0)


def draw_glow_circle(
    frame: np.ndarray,
    center: tuple,
    radius: int,
    color: tuple,
    layers: int = 4,
    thickness: int = 2,
) -> None:
    """Draw a glowing circle by rendering multiple concentric circles with decreasing opacity."""
    overlay = frame.copy()
    for i in range(layers, 0, -1):
        glow_alpha = 0.15 * i / layers
        glow_radius = radius + (layers - i) * 6
        cv2.circle(overlay, center, glow_radius, color, thickness + i)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    cv2.circle(frame, center, radius, color, thickness)


def draw_glow_line(
    frame: np.ndarray,
    pt1: tuple,
    pt2: tuple,
    color: tuple,
    thickness: int = 3,
    layers: int = 4,
) -> None:
    """Draw a glowing line."""
    overlay = frame.copy()
    for i in range(layers, 0, -1):
        glow_alpha = 0.15 * i / layers
        cv2.line(overlay, pt1, pt2, color, thickness + (layers - i) * 3)
    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
    cv2.line(frame, pt1, pt2, color, thickness)


def lerp_color(c1: tuple, c2: tuple, t: float) -> tuple:
    """Linear interpolate between two BGR colors."""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def landmark_to_pixel(landmark, frame_shape: tuple) -> tuple:
    """Convert a MediaPipe NormalizedLandmark to pixel coordinates."""
    h, w = frame_shape[:2]
    return int(landmark.x * w), int(landmark.y * h)


def hand_center(hand_landmarks, frame_shape: tuple) -> tuple:
    """Return the centroid of all 21 hand landmarks in pixel space."""
    h, w = frame_shape[:2]
    xs = [lm.x * w for lm in hand_landmarks.landmark]
    ys = [lm.y * h for lm in hand_landmarks.landmark]
    return int(np.mean(xs)), int(np.mean(ys))
