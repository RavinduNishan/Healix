import subprocess
import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

cmd = [
    "rpicam-vid",
    "-t", "0",
    "--width", "640",
    "--height", "480",
    "--framerate", "15",
    "--codec", "mjpeg",
    "-o", "-"
]

process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    bufsize=0
)

buffer = b""

while True:
    buffer += process.stdout.read(4096)

    start = buffer.find(b'\xff\xd8')
    end = buffer.find(b'\xff\xd9')

    if start != -1 and end != -1 and end > start:
        jpg = buffer[start:end+2]
        buffer = buffer[end+2:]

        frame = cv2.imdecode(
            np.frombuffer(jpg, dtype=np.uint8),
            cv2.IMREAD_COLOR
        )

        if frame is not None:
            results = model(frame, conf=0.5)

            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    if model.names[cls] == "bottle":
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cx = (x1 + x2) // 2
                        cy = (y1 + y2) // 2

                        cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
                        cv2.circle(frame, (cx,cy), 5, (0,0,255), -1)
                        cv2.putText(frame, "Bottle",
                                    (x1, y1-10),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.6, (0,255,0), 2)

                        print(f"Bottle center: {cx}, {cy}")

            cv2.imshow("Bottle Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

process.terminate()
cv2.destroyAllWindows()
