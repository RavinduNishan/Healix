#!/usr/bin/env python3
"""
Biscuit Handover Main Controller
=================================
1. Move camera to biscuit viewing position (channel 5 = 161)
2. Detect how many biscuits are available using YOLO model
3. Move camera back to home position
4. Run the appropriate handover script based on count:
   - 3 biscuits -> smart_biscuit_handover.py  (give_biscuit3.json)
   - 2 biscuits -> smart_biscuit_handover2.py (give_biscuit2.json)
   - 1 biscuit  -> smart_biscuit_handover3.py (give_biscuit1.json)
"""

import os
import time
import sys
import cv2
from ultralytics import YOLO
from adafruit_servokit import ServoKit
from picamera2 import Picamera2

# ========== CONFIGURATION ==========
MODEL_PATH = "models/best.pt"
CAMERA_HOME = 93         # Camera home angle (channel 5)
CAMERA_BISCUIT = 161     # Camera angle to view biscuits
CAMERA_CHANNEL = 5
DETECTION_CONFIDENCE = 0.6
DETECTION_FRAMES = 10    # Number of frames to sample for reliable detection
CAMERA_MOVE_DELAY = 0.02 # Delay per degree when moving camera
CAMERA_SETTLE_TIME = 2   # Wait for camera to settle after moving
# ====================================

# Initialize servo kit
kit = ServoKit(channels=16)
kit.servo[0].set_pulse_width_range(450, 2550)

# Set all servos to home position
HOME_ANGLES = {0: 90, 1: 147, 2: 180, 3: 124, 4: 0, 5: CAMERA_HOME}
print("Setting home position...")
for ch, ang in HOME_ANGLES.items():
    kit.servo[ch].angle = ang
    time.sleep(0.2)


def move_camera(target_angle):
    """Smoothly move camera servo to target angle."""
    current = int(kit.servo[CAMERA_CHANNEL].angle)
    step = 1 if target_angle > current else -1
    for angle in range(current, target_angle + step, step):
        kit.servo[CAMERA_CHANNEL].angle = angle
        time.sleep(CAMERA_MOVE_DELAY)


def detect_biscuit_count():
    """
    Capture multiple frames and determine biscuit count using YOLO model.
    Returns the most frequently detected class name, or None.
    """
    model = YOLO(MODEL_PATH)

    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    time.sleep(CAMERA_SETTLE_TIME)

    detections = []
    print(f"   Capturing {DETECTION_FRAMES} frames for detection...")

    for i in range(DETECTION_FRAMES):
        frame = picam2.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        results = model(frame_bgr, imgsz=320, conf=DETECTION_CONFIDENCE, verbose=False)

        # Draw detection results on frame
        annotated = results[0].plot()

        if results[0].boxes and len(results[0].boxes) > 0:
            # Get the highest confidence detection
            best_idx = results[0].boxes.conf.argmax()
            cls_id = int(results[0].boxes.cls[best_idx])
            cls_name = results[0].names[cls_id]
            detections.append(cls_name)
            print(f"   Frame {i+1}: {cls_name} (conf: {results[0].boxes.conf[best_idx]:.2f})")
        else:
            print(f"   Frame {i+1}: no detection")

        cv2.imshow("Biscuit Detection", annotated)
        cv2.waitKey(1)

        time.sleep(0.3)

    cv2.destroyAllWindows()
    picam2.stop()

    if not detections:
        return None

    # Return most common detection
    from collections import Counter
    most_common = Counter(detections).most_common(1)[0]
    print(f"\n   Detection result: {most_common[0]} ({most_common[1]}/{DETECTION_FRAMES} frames)")
    return most_common[0]


# ============================================================
# MAIN EXECUTION
# ============================================================

print("\n" + "=" * 70)
print("BISCUIT HANDOVER CONTROLLER")
print("=" * 70)

# Step 1: Move camera to biscuit viewing position
print(f"\nMoving camera to biscuit position ({CAMERA_BISCUIT} degrees)...")
move_camera(CAMERA_BISCUIT)
time.sleep(CAMERA_SETTLE_TIME)

# Step 2: Detect biscuit count
print("\nDetecting biscuit count...")
detected_class = detect_biscuit_count()

# Step 3: Move camera back to home
print(f"\nMoving camera back to home ({CAMERA_HOME} degrees)...")
move_camera(CAMERA_HOME)

# Step 4: Decide which handover to run
print("\n" + "=" * 70)

script = None

if detected_class == "three_biscuit":
    print("3 biscuits detected -> Running handover with give_biscuit3.json")
    script = "smart_biscuit_handover.py"

elif detected_class == "two_biscuit":
    print("2 biscuits detected -> Running handover with give_biscuit2.json")
    script = "smart_biscuit_handover2.py"

elif detected_class == "one_biscuit":
    print("1 biscuit detected -> Running handover with give_biscuit1.json")
    script = "smart_biscuit_handover3.py"

else:
    print(f"No biscuit detected (result: {detected_class})")

print("=" * 70)

if script:
    print(f"\nLaunching {script}...\n")
    # Replace this process with the handover script so there are no
    # conflicting servo/camera connections
    os.execvp(sys.executable, [sys.executable, script])
else:
    print("\nDone.")
