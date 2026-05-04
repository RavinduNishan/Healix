#!/usr/bin/env python3
"""
Simple Hand Detection using MediaPipe
=====================================
This script captures video from the camera, detects any hands present
in the frame, and draws the hand landmarks.

- Press 'q' to quit the program.
"""

import cv2
import mediapipe as mp
import time
from picamera2 import Picamera2

# ========== CONFIGURATION ==========
# You can adjust these confidence values
DETECTION_CONFIDENCE = 0.5  # Minimum confidence value for hand detection
TRACKING_CONFIDENCE = 0.5   # Minimum confidence value for hand tracking
MAX_HANDS = 2               # Maximum number of hands to detect
SHOW_CAMERA_WINDOW = True   # Set to False if running without a display

# ====================================

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=MAX_HANDS,
    min_detection_confidence=DETECTION_CONFIDENCE,
    min_tracking_confidence=TRACKING_CONFIDENCE
)

# Initialize camera
print("📷 Initializing camera...")
try:
    picam2 = Picamera2()
    # Set ScalerCrop to use the full sensor area to "zoom out"
    full_resolution = picam2.sensor_resolution
    picam2.set_controls({"ScalerCrop": (0, 0, full_resolution[0], full_resolution[1])})
    picam2.preview_configuration.main.size = (640, 480)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.configure("preview")
    picam2.start()
    time.sleep(2.0)  # Allow camera to warm up
    print("✅ Camera initialized successfully.")
except Exception as e:
    print(f"❌ Failed to initialize camera: {e}")
    exit(1)

# ============================================================
# MAIN EXECUTION
# ============================================================

print("\n" + "=" * 50)
print("👋 HAND DETECTION TEST")
print("=" * 50)
print("Show your hand to the camera.")
print("Press 'q' to quit.")

try:
    while True:
        # Capture a frame from the camera
        frame = picam2.capture_array()
        if frame is None:
            print("⚠️ Failed to capture frame.")
            time.sleep(0.5)
            continue

        # Flip the frame horizontally for a more intuitive selfie-view
        frame = cv2.flip(frame, 1)

        # Convert the BGR image to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame and find hands
        results = hands.process(rgb_frame)

        # Draw the hand annotations on the frame
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )
            cv2.putText(frame, "Hand Detected", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "No Hand Detected", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Display the resulting frame
        if SHOW_CAMERA_WINDOW:
            cv2.imshow('Hand Detection Test', frame)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Cleanup
    print("\n🧹 Cleaning up...")
    picam2.stop()
    hands.close()
    cv2.destroyAllWindows()
    print("✅ Program finished.")
