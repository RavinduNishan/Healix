import cv2
import subprocess
import numpy as np

proc = subprocess.Popen(
    ["rpicam-vid", "--width", "640", "--height", "480", "--codec", "mjpeg", "-o", "-"],
    stdout=subprocess.PIPE, bufsize=0
)

buffer = b""
while True:
    buffer += proc.stdout.read(1024)
    a = buffer.find(b'\xff\xd8')
    b = buffer.find(b'\xff\xd9')
    if a != -1 and b != -1:
        jpg = buffer[a:b+2]
        buffer = buffer[b+2:]
        frame = cv2.imdecode(np.frombuffer(jpg, np.uint8), 1)
        cv2.imshow("Camera Test", frame)
    if cv2.waitKey(1) == ord('q'):
        break
