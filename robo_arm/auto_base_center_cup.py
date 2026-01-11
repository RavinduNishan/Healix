import os
os.environ["ULTRALYTICS_OFFLINE"] = "1"

import cv2
import subprocess
import numpy as np
import time
from ultralytics import YOLO
from adafruit_servokit import ServoKit

# =============================
# CONFIG
# =============================
MODEL_PATH = "/home/isuru/Healix/robo_arm/cup_dataset/models/best.pt"

# Servo (BASE only)
BASE_CH = 0
BASE_ANGLE = 130
BASE_MIN = 20
BASE_MAX = 160

# Camera
FRAME_W = 416
FRAME_H = 416

# Detection
CONF = 0.25
CENTER_TOLERANCE = 15  # pixels
STEP = 1               # degree per move
DELAY = 0.04           # smooth motion delay

# =============================
# CAMERA OFFSET (IMPORTANT)
# Camera is 8 cm in front of base
# =============================
CAMERA_FORWARD_CM = 8
CAMERA_OFFSET_PX = 30   # 🔧 Tune 20–40 if needed

ARM_CENTER_X = (FRAME_W // 2) + CAMERA_OFFSET_PX

# =============================
# LOAD MODEL
# =============================
model = YOLO(MODEL_PATH)
print("✅ Model loaded")
print("📦 Classes:", model.names)

# =============================
# SERVO INIT
# =============================
print("🔌 Power ON servos, then press ENTER")
input()

kit = ServoKit(channels=16)
kit.servo[BASE_CH].angle = BASE_ANGLE
time.sleep(1)

print(f"🔄 Base initialized at {BASE_ANGLE}°")

# =============================
# CAMERA PIPELINE
# =============================
proc = subprocess.Popen(
    [
        "rpicam-vid",
        "--rotation", "180",
        "--width", str(FRAME_W),
        "--height", str(FRAME_H),
        "--framerate", "8",
        "--codec", "mjpeg",
        "-o", "-"
    ],
    stdout=subprocess.PIPE,
    bufsize=0
)

buffer = b""
print("📷 Detecting cup and centering base")

# =============================
# MAIN LOOP
# =============================
try:
    while True:
        buffer += proc.stdout.read(1024)

        start = buffer.find(b'\xff\xd8')
        end = buffer.find(b'\xff\xd9')
        if start == -1 or end == -1:
            continue

        jpg = buffer[start:end + 2]
        buffer = buffer[end + 2:]

        frame = cv2.imdecode(
            np.frombuffer(jpg, np.uint8),
            cv2.IMREAD_COLOR
        )
        if frame is None:
            continue

        # YOLO detection
        results = model(frame, imgsz=416, conf=CONF, verbose=False)

        # Draw arm center (offset compensated)
        cv2.line(
            frame,
            (ARM_CENTER_X, 0),
            (ARM_CENTER_X, FRAME_H),
            (0, 0, 255),
            2
        )

        detected = False

        for r in results:
            if r.boxes is None:
                continue

            for box in r.boxes:
                cls_id = int(box.cls[0])
                if model.names[cls_id] != "cup":
                    continue

                detected = True

                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                error = cx - ARM_CENTER_X

                # Draw detection
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

                cv2.putText(
                    frame,
                    f"Base:{BASE_ANGLE} Err:{error}px Off:{CAMERA_OFFSET_PX}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
                )

                # BASE ROTATION
                if abs(error) > CENTER_TOLERANCE:
                    if error > 0:
                        BASE_ANGLE -= STEP
                    else:
                        BASE_ANGLE += STEP

                    BASE_ANGLE = max(BASE_MIN, min(BASE_MAX, BASE_ANGLE))
                    kit.servo[BASE_CH].angle = BASE_ANGLE
                    time.sleep(DELAY)

                else:
                    cv2.putText(
                        frame,
                        "CUP CENTERED",
                        (120, FRAME_H - 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 0),
                        2
                    )

                break  # Only track one cup

        if not detected:
            cv2.putText(
                frame,
                "SEARCHING...",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

        cv2.imshow("Cup Detection + Base Centering", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    pass

# =============================
# CLEAN EXIT
# =============================
proc.terminate()
cv2.destroyAllWindows()
print("🛑 Finished")
