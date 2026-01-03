import os
os.environ["ULTRALYTICS_OFFLINE"] = "1"
os.environ["QT_QPA_PLATFORM"] = "xcb"   # fix Qt warning

from ultralytics import YOLO
import cv2
import subprocess
import numpy as np

# ==================================================
# LOAD MODEL (YOUR CONFIRMED PATH)
# ==================================================
MODEL_PATH = "/home/isuru/Healix/robo_arm/cup_dataset/models/best.pt"
model = YOLO(MODEL_PATH)

print("✅ Model loaded")
print("📦 Classes:", model.names)

# ==================================================
# CAMERA SETTINGS (MATCH MODEL SIZE)
# ==================================================
WIDTH = 416
HEIGHT = 416

cmd = [
    "rpicam-vid",
    "--rotation", "180",
    "--width", str(WIDTH),
    "--height", str(HEIGHT),
    "--framerate", "8",
    "--codec", "mjpeg",
    "-o", "-"
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=0)
buffer = b""

print("📷 Camera started")
print("👉 Hold the cup still for 2–3 seconds")
print("❌ Ctrl + C to quit")

frame_count = 0

# ==================================================
# MAIN LOOP
# ==================================================
while True:
    buffer += proc.stdout.read(1024)

    start = buffer.find(b'\xff\xd8')
    end = buffer.find(b'\xff\xd9')

    if start != -1 and end != -1:
        jpg = buffer[start:end+2]
        buffer = buffer[end+2:]

        frame = cv2.imdecode(
            np.frombuffer(jpg, np.uint8),
            cv2.IMREAD_COLOR
        )

        if frame is None:
            continue

        frame_count += 1
        if frame_count % 3 != 0:
            continue

        # ==================================================
        # YOLO DETECTION (FORCED img size)
        # ==================================================
        results = model(
            frame,
            imgsz=416,     # 🔥 VERY IMPORTANT
            conf=0.15,     # balanced confidence
            iou=0.5,
            max_det=1
        )

        boxes = results[0].boxes

        if boxes is not None and len(boxes) > 0:
            box = boxes[0]
            x1, y1, x2, y2 = box.xyxy[0]

            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)
            h = int(y2 - y1)

            print(f"🟢 CUP DETECTED → center=({cx},{cy}) height={h}px")
        else:
            print("⚪ No cup detected")

        # OPTIONAL: comment this out if GUI causes issues
        annotated = results[0].plot()
        cv2.imshow("Cup Detection", annotated)
        cv2.waitKey(1)

# ==================================================
# CLEAN EXIT
# ==================================================
proc.terminate()
cv2.destroyAllWindows()
