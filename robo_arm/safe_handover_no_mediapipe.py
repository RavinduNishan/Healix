import cv2
import numpy as np
import time
from picamera2 import Picamera2

# -------------------------
# Camera Setup (Full FOV)
# -------------------------
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

# Full sensor field of view (IMX219)
picam2.set_controls({"ScalerCrop": (0, 0, 3280, 2464)})

bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=50)

handover_timer = None
REQUIRED_STABLE_TIME = 2  # seconds

print("🟢 Healix Open-Palm Detection Started")

while True:
    frame = picam2.capture_array()
    frame = cv2.flip(frame, 1)

    fg_mask = bg_subtractor.apply(frame)
    fg_mask = cv2.GaussianBlur(fg_mask, (5, 5), 0)
    _, thresh = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    palm_detected = False
    safe_zone = False

    # Safe zone box
    x1, y1, x2, y2 = 220, 150, 420, 350
    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

    if contours:
        max_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(max_contour)

        # Open palm should have large area
        if area > 6000:   # adjust if needed
            palm_detected = True
            cv2.drawContours(frame, [max_contour], -1, (0, 255, 0), 2)

            M = cv2.moments(max_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

                if x1 < cx < x2 and y1 < cy < y2:
                    safe_zone = True

    # -------------------------
    # Safe Release Logic
    # -------------------------
    if palm_detected and safe_zone:
        if handover_timer is None:
            handover_timer = time.time()
        elif time.time() - handover_timer > REQUIRED_STABLE_TIME:
            print("✅ Safe to Release!")
            break
    else:
        handover_timer = None

    cv2.putText(frame, f"Area: {int(area) if contours else 0}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Healix Safe Handover", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()