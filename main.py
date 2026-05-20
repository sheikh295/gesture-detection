"""Main entry point — opens webcam, runs detection loop, overlays effects."""

import time
import cv2
import numpy as np

from gesture_detector import GestureDetector
from effects import EffectManager
from config import (
    CAMERA_INDEX,
    FRAME_WIDTH,
    FRAME_HEIGHT,
    EFFECT_FADE_FRAMES,
    HUD_COLOR,
    HUD_FONT_SCALE,
    HUD_THICKNESS,
    FPS_COLOR,
)

GESTURE_LEGEND = [
    ("OPEN_PALM", "Spirit Bomb"),
    ("FIST",      "Fire"),
    ("POINTING",  "Sword"),
    ("PEACE",     "Ki Shield"),
    ("PINCH",     "Kamehameha"),
    ("HORNS",     "SSJ Aura"),
]


def draw_hud(frame: np.ndarray, gesture: str, fps: float) -> None:
    h, w = frame.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX

    # --- Gesture name top-left ---
    label = gesture if gesture not in ("NONE", None) else "DETECTING..."
    cv2.putText(frame, label, (20, 50), font, 1.2, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(frame, label, (20, 50), font, 1.2, HUD_COLOR, 2, cv2.LINE_AA)

    # --- FPS top-right ---
    fps_text = f"FPS: {fps:.0f}"
    (fw, fh), _ = cv2.getTextSize(fps_text, font, 0.7, 2)
    cv2.putText(frame, fps_text, (w - fw - 15, 40), font, 0.7, FPS_COLOR, 2, cv2.LINE_AA)

    # --- Legend strip bottom ---
    legend_y = h - 20
    cell_w = w // len(GESTURE_LEGEND)
    for i, (gname, gdesc) in enumerate(GESTURE_LEGEND):
        x = i * cell_w + 10
        color = (0, 255, 255) if gesture == gname else (160, 160, 160)
        cv2.putText(frame, f"{gname}:{gdesc}", (x, legend_y), font, 0.38, color, 1, cv2.LINE_AA)

    # --- No hand detected banner ---
    if gesture in ("NONE", None):
        text = "SHOW HAND TO BEGIN"
        (tw, th), _ = cv2.getTextSize(text, font, 1.0, 2)
        tx = (w - tw) // 2
        ty = h // 2
        cv2.putText(frame, text, (tx, ty), font, 1.0, (60, 60, 60), 3, cv2.LINE_AA)
        cv2.putText(frame, text, (tx, ty), font, 1.0, (180, 180, 180), 1, cv2.LINE_AA)


def open_camera() -> cv2.VideoCapture:
    """Try camera index 0, fall back to 1."""
    for idx in (CAMERA_INDEX, 1):
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
            return cap
    raise RuntimeError("Could not open any camera. Check permissions.")


def main() -> None:
    cap = open_camera()
    detector = GestureDetector()
    effect_manager = EffectManager(fade_frames=EFFECT_FADE_FRAMES)

    prev_time = time.perf_counter()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame — exiting.")
            break

        frame = cv2.flip(frame, 1)  # mirror for natural feel

        gesture, landmarks = detector.detect(frame)
        effect_manager.update(gesture, frame, landmarks)
        effect_manager.draw(frame)

        # FPS calculation
        now = time.perf_counter()
        fps = 1.0 / max(now - prev_time, 1e-6)
        prev_time = now

        draw_hud(frame, gesture, fps)

        cv2.imshow("DBZ Gestures", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
