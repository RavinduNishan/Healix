from picamera2 import Picamera2
import cv2
import mediapipe as mp
import time

# -------------------------
# CAMERA SETUP
# -------------------------
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
picam2.start()

# -------------------------
# MEDIAPIPE HANDS
# -------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

handover_timer = None
REQUIRED_STABLE_TIME = 2  # seconds

print("🟢 Smart Handover System Started")

# -------------------------
# MAIN LOOP
# -------------------------
while True:
    frame = picam2.capture_array()
    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    hand_detected = False
    fingers_open = False

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get finger tip positions
            tips = [8, 12, 16, 20]  # index, middle, ring, pinky
            open_count = 0

            for tip in tips:
                if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
                    open_count += 1

            if open_count >= 3:
                fingers_open = True

            # Handover zone (center box)
            cx = hand_landmarks.landmark[9].x * 640
            cy = hand_landmarks.landmark[9].y * 480

            if 220 < cx < 420 and 150 < cy < 350:
                hand_detected = True

    # -------------------------
    # SAFE RELEASE LOGIC
    # -------------------------
    if hand_detected and fingers_open:
        if handover_timer is None:
            handover_timer = time.time()
        elif time.time() - handover_timer > REQUIRED_STABLE_TIME:
            print("✅ Safe to Release!")
            # 👉 CALL YOUR GRIPPER RELEASE FUNCTION HERE
            break
    else:
        handover_timer = None

    cv2.rectangle(frame, (220,150), (420,350), (0,255,0), 2)
    cv2.imshow("Healix Smart Handover", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()