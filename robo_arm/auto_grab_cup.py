import time
import os
os.environ["ULTRALYTICS_OFFLINE"] = "1"

from ultralytics import YOLO
from adafruit_servokit import ServoKit
import cv2
import subprocess
import numpy as np
from collections import deque

# ==========================
# CONFIG
# ==========================
FRAME = 416
CONF = 0.15

BASE, SHOULDER, ELBOW, WRIST, GRIPPER = 0,1,2,3,4

HOME = {
    BASE: 90,
    SHOULDER: 35,
    ELBOW: 90,
    WRIST: 90,
    GRIPPER: 90
}

GRIPPER_CLOSE = 40

# ==========================
# LOAD YOLO (NO SERVOS)
# ==========================
model = YOLO("yolov8n.pt")
print("✅ YOLO loaded")
print("🚫 SERVO POWER MUST BE OFF")

# ==========================
# CAMERA
# ==========================
proc = subprocess.Popen([
    "rpicam-vid",
    "--rotation","180",
    "--width",str(FRAME),
    "--height",str(FRAME),
    "--framerate","8",
    "--codec","mjpeg",
    "-o","-"
], stdout=subprocess.PIPE, bufsize=0)

buffer = b""

# ==========================
# DETECTION LOCK
# ==========================
cx_hist = deque(maxlen=8)
h_hist = deque(maxlen=8)
stable = 0
LOCK = 8
target = None

print("🔍 Detecting cup…")

while target is None:
    buffer += proc.stdout.read(1024)
    a = buffer.find(b'\xff\xd8')
    b = buffer.find(b'\xff\xd9')
    if a != -1 and b != -1:
        jpg = buffer[a:b+2]
        buffer = buffer[b+2:]
        frame = cv2.imdecode(np.frombuffer(jpg,np.uint8),1)
        if frame is None: continue

        r = model(frame, imgsz=FRAME, conf=CONF, max_det=1)
        boxes = r[0].boxes

        if boxes:
            x1,y1,x2,y2 = boxes[0].xyxy[0]
            cx = int((x1+x2)/2)
            h  = int(y2-y1)
            cx_hist.append(cx)
            h_hist.append(h)
            stable += 1
            print(f"🟢 stable {stable}")
        else:
            stable = 0
            cx_hist.clear()
            h_hist.clear()

        if stable >= LOCK:
            target = (
                sum(cx_hist)//len(cx_hist),
                sum(h_hist)//len(h_hist)
            )

# ==========================
# SERVO ARMING PHASE
# ==========================
print("\n🎯 CUP LOCKED")
print("🔌 TURN SERVO POWER ON **NOW**")
print("⏳ WAITING 3 SECONDS…")
time.sleep(3)

# Initialize ServoKit AFTER power is ON
kit = ServoKit(channels=16)

# WRITE HOME ANGLES IMMEDIATELY
for ch, ang in HOME.items():
    kit.servo[ch].angle = ang

print("✅ Servos synchronized — NO JUMP POSSIBLE")
time.sleep(1)

# ==========================
# SLOW MOVE FUNCTION
# ==========================
def move_slow(ch, target, step=1, delay=0.05):
    cur = int(kit.servo[ch].angle)
    step = step if target > cur else -step
    for a in range(cur, target, step):
        kit.servo[ch].angle = a
        time.sleep(delay)
    kit.servo[ch].angle = target

# ==========================
# COMPUTE TARGET
# ==========================
cx, h = target
base = int(90 + (cx - FRAME/2) * 0.12)
base = max(30, min(150, base))

# ==========================
# MOVE — VERY SLOW
# ==========================
print("🤖 MOVING SLOWLY — NO JUMP")
move_slow(GRIPPER, 90)
move_slow(BASE, base)
move_slow(SHOULDER, 55)
move_slow(ELBOW, 70)
move_slow(WRIST, 90)

time.sleep(0.5)
move_slow(GRIPPER, GRIPPER_CLOSE)

print("🥤 CUP GRABBED")

# ==========================
# RETURN HOME
# ==========================
move_slow(ELBOW, HOME[ELBOW])
move_slow(SHOULDER, HOME[SHOULDER])
move_slow(BASE, HOME[BASE])

print("✅ DONE — ZERO JUMP")
