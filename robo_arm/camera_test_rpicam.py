import subprocess
import cv2
import numpy as np

# Start rpicam MJPEG stream
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

    # Look for JPEG start/end
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
            cv2.imshow("Pi Camera (rpicam)", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

process.terminate()
cv2.destroyAllWindows()
