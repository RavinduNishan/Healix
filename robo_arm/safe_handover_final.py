import cv2
import time
import numpy as np
from picamera2 import Picamera2
import mediapipe as mp

# -----------------------------
# MediaPipe Setup
# -----------------------------
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# -----------------------------
# Camera Setup
# -----------------------------
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

# Full sensor FOV
picam2.set_controls({"ScalerCrop": (0, 0, 3280, 2464)})

handover_timer = None
REQUIRED_STABLE_TIME = 2

print("🟢 Healix Professional Palm Detection Started")

while True:
    frame = picam2.capture_array()
    frame = cv2.flip(frame, 1)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    safe_zone = False
    palm_open = False

    # Safe Zone Box
    x1, y1, x2, y2 = 220, 150, 420, 350
    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            landmarks = hand_landmarks.landmark

            # Palm center (wrist landmark)
            wrist = landmarks[0]
            cx = int(wrist.x * 640)
            cy = int(wrist.y * 480)

            cv2.circle(frame, (cx, cy), 6, (0, 0, 255), -1)

            # Check safe zone
            if x1 < cx < x2 and y1 < cy < y2:
                safe_zone = True

            # Check open palm:
            # Compare fingertip y vs knuckle y (extended finger = smaller y)
            finger_tips = [8, 12, 16, 20]
            finger_pips = [6, 10, 14, 18]

            extended_fingers = 0

            for tip, pip in zip(finger_tips, finger_pips):
                if landmarks[tip].y < landmarks[pip].y:
                    extended_fingers += 1

            if extended_fingers >= 3:
                palm_open = True

    # -------------------------
    # Safe Release Logic
    # -------------------------
    if palm_open and safe_zone:
        if handover_timer is None:
            handover_timer = time.time()
        elif time.time() - handover_timer > REQUIRED_STABLE_TIME:
            print("✅ SAFE TO RELEASE")
            break
    else:
        handover_timer = None

    cv2.putText(frame, f"Palm Open: {palm_open}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Healix Safe Handover", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()