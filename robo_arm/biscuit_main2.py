#!/usr/bin/env python3

import time
import sys
import cv2
from ultralytics import YOLO
from adafruit_servokit import ServoKit
from picamera2 import Picamera2
from collections import Counter

# ========== CONFIGURATION ==========
MODEL_PATH = "models/best.pt"
CAMERA_HOME = 83
CAMERA_BISCUIT = 133
CAMERA_CHANNEL = 5
DETECTION_CONFIDENCE = 0.6
DETECTION_FRAMES = 10
CAMERA_MOVE_DELAY = 0.02
CAMERA_SETTLE_TIME = 2
# ==================================

# Initialize servo
kit = ServoKit(channels=16)

HOME_ANGLES = {0: 90, 1: 147, 2: 180, 3: 124, 4: 0, 5: CAMERA_HOME}

# Move all servos to home
for ch, ang in HOME_ANGLES.items():
    kit.servo[ch].angle = ang
    time.sleep(0.2)


def move_camera(target_angle):
    current = int(kit.servo[CAMERA_CHANNEL].angle)
    step = 1 if target_angle > current else -1
    for angle in range(current, target_angle + step, step):
        kit.servo[CAMERA_CHANNEL].angle = angle
        time.sleep(CAMERA_MOVE_DELAY)


def detect_biscuit_count():
    model = YOLO(MODEL_PATH)

    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    time.sleep(CAMERA_SETTLE_TIME)

    detections = []

    for i in range(DETECTION_FRAMES):
        frame = picam2.capture_array()
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        results = model(frame_bgr, imgsz=320, conf=DETECTION_CONFIDENCE, verbose=False)

        if results[0].boxes and len(results[0].boxes) > 0:
            best_idx = results[0].boxes.conf.argmax()
            cls_id = int(results[0].boxes.cls[best_idx])
            cls_name = results[0].names[cls_id]
            detections.append(cls_name)

        time.sleep(0.3)

    picam2.stop()

    if not detections:
        return None

    most_common = Counter(detections).most_common(1)[0]
    return most_common[0]


# ================= MAIN =================

# Move camera to biscuit view
move_camera(CAMERA_BISCUIT)
time.sleep(CAMERA_SETTLE_TIME)

# Detect
detected_class = detect_biscuit_count()

# Move back home
move_camera(CAMERA_HOME)

# Print result for Flask
if detected_class == "three_biscuit":
    print("3 biscuits detected")
elif detected_class == "two_biscuit":
    print("2 biscuits detected")
elif detected_class == "one_biscuit":
    print("1 biscuit detected")
else:
    print("No biscuit detected")