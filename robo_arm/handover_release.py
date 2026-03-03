import cv2
import time
import numpy as np
from picamera2 import Picamera2
from adafruit_servokit import ServoKit

# =========================
# SERVO SETUP
# =========================
GRIPPER = 4
kit = ServoKit(channels=16)

grip_closed = 20
grip_open = 80
kit.servo[GRIPPER].angle = grip_closed

# =========================
# CAMERA SETUP
# =========================
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()

# =========================
# HANDOVER ZONE
# =========================
zone_x1, zone_y1 = 220, 150
zone_x2, zone_y2 = 420, 350

hand_detected_time = None
required_hold_time = 2  # seconds

print("Waiting for hand in zone...")

while True:
    frame = picam2.capture_array()
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

    # Skin color range (can adjust if needed)
    lower_skin = np.array([0, 30, 60])
    upper_skin = np.array([20, 150, 255])

    mask = cv2.inRange(hsv, lower_skin, upper_skin)
    mask = cv2.GaussianBlur(mask, (5, 5), 0)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    hand_in_zone = False

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 3000:
            x, y, w, h = cv2.boundingRect(cnt)
            center_x = x + w // 2
            center_y = y + h // 2

            if zone_x1 < center_x < zone_x2 and zone_y1 < center_y < zone_y2:
                hand_in_zone = True
                cv2.rectangle(frame_bgr, (x, y), (x+w, y+h), (0,255,0), 2)

    # Draw handover zone
    cv2.rectangle(frame_bgr, (zone_x1, zone_y1), (zone_x2, zone_y2), (255,0,0), 2)

    if hand_in_zone:
        if hand_detected_time is None:
            hand_detected_time = time.time()

        elapsed = time.time() - hand_detected_time
        cv2.putText(frame_bgr, f"Hold: {elapsed:.1f}s", (10,40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        if elapsed >= required_hold_time:
            print("Releasing cup safely...")

            # Slow release
            for angle in range(grip_closed, grip_open, 2):
                kit.servo[GRIPPER].angle = angle
                time.sleep(0.05)

            break
    else:
        hand_detected_time = None

    cv2.imshow("Handover System", frame_bgr)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()