# Configuration constants for DBZ Gesture Detection

# Gesture detection
GESTURE_HOLD_FRAMES = 5       # consecutive frames before effect triggers
PINCH_DISTANCE_THRESHOLD = 40  # pixels; thumb-index distance for PINCH

# Particle / effect parameters
PARTICLE_COUNT = 30
SWORD_LENGTH = 280            # pixels
SHIELD_RADIUS = 120

# Effect fade frames when gesture changes
EFFECT_FADE_FRAMES = 10

# Camera
CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# MediaPipe
MAX_NUM_HANDS = 2
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.7

# Colors (BGR)
EFFECT_COLORS = {
    "FIST":      (0, 100, 255),   # fire orange-red
    "OPEN_PALM": (255, 200, 0),   # spirit bomb blue-white
    "POINTING":  (255, 255, 0),   # sword cyan
    "PEACE":     (0, 255, 150),   # shield green
    "PINCH":     (255, 50, 0),    # kamehameha blue
    "HORNS":     (0, 200, 255),   # aura gold
}

HUD_COLOR = (200, 200, 255)
HUD_FONT_SCALE = 0.8
HUD_THICKNESS = 2
FPS_COLOR = (0, 255, 0)
