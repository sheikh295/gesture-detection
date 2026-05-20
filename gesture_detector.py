"""MediaPipe hand tracking and gesture classification."""

import math
import mediapipe as mp
import numpy as np
from config import (
    MAX_NUM_HANDS,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    GESTURE_HOLD_FRAMES,
    PINCH_DISTANCE_THRESHOLD,
)


class GestureDetector:
    def __init__(self):
        self._mp_hands = mp.solutions.hands
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_NUM_HANDS,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )
        # Hold-frame counters per gesture
        self._hold_counts: dict[str, int] = {}
        self._last_raw: str = "NONE"
        self._committed_gesture: str = "NONE"
        self._all_landmarks = []  # list of hand_landmarks per detected hand

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect(self, frame):
        """
        Run hand detection on *frame* (BGR).
        Returns (gesture_string, list_of_hand_landmarks).
        gesture_string is the committed gesture after hold-frame debounce.
        """
        import cv2

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb)

        self._all_landmarks = []
        raw_gesture = "NONE"

        if results.multi_hand_landmarks:
            self._all_landmarks = results.multi_hand_landmarks

            # Two-hand gestures take priority
            if len(results.multi_hand_landmarks) == 2:
                g1 = self._classify_gesture(results.multi_hand_landmarks[0])
                g2 = self._classify_gesture(results.multi_hand_landmarks[1])
                if g1 == "PINCH" and g2 == "PINCH":
                    raw_gesture = "PINCH"
                else:
                    raw_gesture = g1 if g1 != "NONE" else g2
            else:
                raw_gesture = self._classify_gesture(results.multi_hand_landmarks[0])

        # Debounce with hold-frame counter
        self._committed_gesture = self._debounce(raw_gesture)
        return self._committed_gesture, self._all_landmarks

    # ------------------------------------------------------------------
    # Gesture classification
    # ------------------------------------------------------------------

    def _classify_gesture(self, hand_landmarks) -> str:
        lm = hand_landmarks.landmark
        fingers = self._finger_states(lm)
        thumb, index, middle, ring, pinky = fingers

        # PINCH — thumb + index close together
        dist = self._distance(lm[4], lm[8])
        if dist < PINCH_DISTANCE_THRESHOLD and not index:
            return "PINCH"

        # OPEN_PALM — all 5 extended
        if all(fingers):
            return "OPEN_PALM"

        # FIST — none extended
        if not any(fingers):
            return "FIST"

        # POINTING — only index
        if not thumb and index and not middle and not ring and not pinky:
            return "POINTING"

        # PEACE / V-SIGN — index + middle
        if not thumb and index and middle and not ring and not pinky:
            return "PEACE"

        # HORNS — index + pinky, middle + ring curled
        if index and not middle and not ring and pinky:
            return "HORNS"

        return "NONE"

    def _finger_states(self, lm) -> list:
        """
        Return [thumb, index, middle, ring, pinky] boolean extended states.
        Thumb uses horizontal axis; others use vertical (tip.y < pip.y).
        """
        # Tip and PIP landmark indices
        tips = [4, 8, 12, 16, 20]
        pips = [3, 6, 10, 14, 18]  # IP for thumb, PIP for rest

        states = []
        for i, (tip_idx, pip_idx) in enumerate(zip(tips, pips)):
            if i == 0:
                # Thumb: compare x positions (mirrored frame)
                states.append(lm[tip_idx].x < lm[pip_idx].x)
            else:
                states.append(lm[tip_idx].y < lm[pip_idx].y)
        return states

    @staticmethod
    def _distance(a, b) -> float:
        """Euclidean distance between two landmarks (normalised coords × 1000)."""
        return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2) * 1000

    # ------------------------------------------------------------------
    # Hold-frame debounce
    # ------------------------------------------------------------------

    def _debounce(self, raw: str) -> str:
        if raw != self._last_raw:
            self._last_raw = raw
            self._hold_counts[raw] = 1
        else:
            self._hold_counts[raw] = self._hold_counts.get(raw, 0) + 1

        if self._hold_counts.get(raw, 0) >= GESTURE_HOLD_FRAMES:
            self._committed_gesture = raw
        return self._committed_gesture
