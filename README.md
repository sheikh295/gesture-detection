# DBZ Gesture Detection

Real-time Dragon Ball Z-style gesture detection app running locally via webcam. Built with Python, OpenCV, and MediaPipe.

## Features

| Gesture | Effect |
|---------|--------|
| ✋ Open Palm | Spirit Bomb — glowing blue energy sphere grows above hand |
| ✊ Fist | Fire — orange/red flame particles erupt from fist |
| ☝️ Pointing | Sword — glowing energy blade extends from index fingertip |
| ✌️ Peace/V-Sign | Ki Shield — translucent rotating aura around hand |
| 🤏 Pinch | Kamehameha — electric blue energy beam fires horizontally |
| 🤘 Horns | Super Saiyan Aura — golden lightning frame-wide effect |

## Project Structure

```
gesture-detection/
├── main.py               # Entry point, main loop
├── gesture_detector.py   # MediaPipe hand tracking + gesture classification
├── effects/
│   ├── __init__.py       # EffectManager
│   ├── base_effect.py    # Abstract base class
│   ├── fire.py           # Fire particle effect
│   ├── spirit_bomb.py    # Spirit bomb effect
│   ├── sword.py          # Energy sword effect
│   ├── shield.py         # Ki shield effect
│   ├── kamehameha.py     # Energy beam effect
│   └── aura.py           # Super Saiyan aura effect
├── utils.py              # Drawing/blending helpers
├── config.py             # Constants, thresholds, colors
└── requirements.txt
```

## Setup

```bash
python -m venv venv
source venv/bin/activate    # macOS/Linux
# venv\Scripts\activate     # Windows

pip install -r requirements.txt
python main.py
```

> **macOS note:** If the camera doesn't open, go to **System Preferences → Privacy & Security → Camera** and grant access to Terminal or your IDE.

## Controls

- Press **`q`** to quit

## Requirements

- Python 3.10+
- Webcam

## How It Works

1. `GestureDetector` uses MediaPipe Hands to track up to 2 hands (21 keypoints each).
2. Finger extension is determined by comparing tip vs. PIP joint positions.
3. A gesture must be held for 5 consecutive frames before triggering an effect (jitter prevention).
4. The `EffectManager` smoothly fades between effects over 10 frames when the gesture changes.
5. All effects are rendered using OpenCV drawing primitives with layered alpha-blending for glow.