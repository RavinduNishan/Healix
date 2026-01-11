import os
os.environ["ULTRALYTICS_OFFLINE"] = "1"

import cv2
import subprocess
import numpy as np
from ultralytics import YOLO

# ============================
# CONFIG
# ============================
FRAME_W = 416
FRAME_H = 416
CONF = 0.05          # very sensitive
IOU = 0.5

# ============================
# LOAD YOLOv8n
# ============================
model = YOLO("yolov8n.pt")
print("✅ YOLOv8n pretrained loaded")

# ============================
# CAMERA (ROTATED 180°)
# ============================
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
print("📷 Camera running continuously (press Q to quit)")

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

        # ----------------------------
        # YOLO DETECTION
        # ----------------------------
        results = model(
            frame,
            imgsz=640,
            conf=CONF,
            iou=IOU,
            verbose=False
        )

        detected = False

        for r in results:
            if r.boxes is None:
                continue

            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id]

                if label != "cup":
                    continue

                detected = True
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf_val = float(box.conf[0])

                cv2.rectangle(frame, (x1, y1), (x2, y2),
                              (0, 255, 0), 2)

                cv2.putText(
                    frame,
                    f"CUP {conf_val:.2f}",
                    (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

        if not detected:
            cv2.putText(
                frame,
                "SEARCHING FOR CUP...",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

        cv2.imshow("YOLOv8n Cup Detection (Continuous)", frame)

        # ❗ ONLY user can stop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("🛑 Quit requested by user")
            break

except KeyboardInterrupt:
    print("🛑 Stopped by Ctrl+C")

# ============================
# CLEAN EXIT (ONLY HERE)
# ============================
proc.terminate()
cv2.destroyAllWindows()
print("✅ Camera closed safely")
