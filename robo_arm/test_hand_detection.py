#!/usr/bin/env python3
"""
Hand Detection Test
====================
Standalone test for hand detection using Picamera2 and MediaPipe.
Same camera and detection setup as horizontal_palm_test.py.

Shows camera feed with hand landmarks and horizontal palm detection status.
Press ESC to quit.
"""

import cv2
import mediapipe as mp
import time
from picamera2 import Picamera2

# Configuration
HAND_DETECTION_CONFIDENCE = 0.7
HAND_TRACKING_CONFIDENCE = 0.7

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=HAND_DETECTION_CONFIDENCE,
    min_tracking_confidence=HAND_TRACKING_CONFIDENCE
)

# Initialize camera (same setup as horizontal_palm_test.py)
print("Initializing camera...")
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()
time.sleep(2)

# Test camera
test_frame = picam2.capture_array()
if test_frame is None or test_frame.size == 0:
    print("Camera test failed!")
    exit(1)
print(f"Camera working - Frame size: {test_frame.shape}")


def fingers_horizontal_extended(hand_landmarks):
    """Check if fingers are in horizontal position with palm facing camera."""
    tips = [8, 12, 16, 20]

    ys = [hand_landmarks.landmark[i].y for i in tips]
    y_diff = max(ys) - min(ys)

    xs = [hand_landmarks.landmark[i].x for i in tips]
    x_spread = max(xs) - min(xs)

    if y_diff <= 0.1 and x_spread >= 0.15:
        return True
    return False


print("\nHand Detection Test Running")
print("Show your horizontal palm to the camera")
print("Press ESC to quit\n")

frame_count = 0
detect_count = 0

while True:
    frame = picam2.capture_array()
    if frame is None:
        continue

    frame_count += 1

    # Convert BGR to RGB for MediaPipe (same as horizontal_palm_test.py)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    status = "No hand detected"
    color = (0, 0, 255)  # Red

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            if fingers_horizontal_extended(hand_landmarks):
                status = "Horizontal palm DETECTED"
                color = (0, 255, 0)  # Green
                detect_count += 1
            else:
                status = "Hand found - not horizontal"
                color = (0, 165, 255)  # Orange

    cv2.putText(frame, status, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    cv2.putText(frame, f"Detections: {detect_count} | Frames: {frame_count}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow("Hand Detection Test", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

print(f"\nResults: {detect_count} horizontal palm detections in {frame_count} frames")

picam2.stop()
hands.close()
cv2.destroyAllWindows()
print("Done")
