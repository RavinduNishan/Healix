import os
os.environ["ULTRALYTICS_OFFLINE"] = "1"

from ultralytics import YOLO
import cv2
import subprocess
import numpy as np

# =========================================
# LOAD PRE-TRAINED YOLOv8 MODEL
# =========================================
model = YOLO("yolov8n.pt")
print("✅ Pretrained model loaded")
print("Classes include:", model.names[41])  # 41 = cup in COCO

# =========================================
# CAMERA SETTINGS (STABLE)
# =========================================
cmd = [
    "rpicam-vid",
    "--rotation", "180",
    "--width", "416",
    "--height", "416",
    "--framerate", "8",
    "--codec", "mjpeg",
    "-o", "-"
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=0)
buffer = b""

print("📷 Camera started")
print("👉 Hold a cup in front of camera")
print("❌ Ctrl + C to quit")

frame_count = 0

# =========================================
# MAIN LOOP
# =========================================
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

        # YOLO DETECTION
        results = model(
            frame,
            imgsz=416,
            conf=0.25,
            iou=0.5,
            classes=[41],   # 🔥 ONLY detect "cup"
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

        annotated = results[0].plot()
        cv2.imshow("Cup Detection (Pretrained)", annotated)
        cv2.waitKey(1)
