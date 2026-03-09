import sys
import time
import tty
import termios
import json
from adafruit_servokit import ServoKit

BASE, SHOULDER, ELBOW, WRIST, GRIPPER = 0, 1, 2, 3, 4
CAM_BASE = 5   # Only camera servo now

angles = {
    BASE: 90,
    SHOULDER: 147,
    ELBOW: 180,
    WRIST: 124,
    GRIPPER: 0,
    CAM_BASE: 91
}

LIMITS = {
    BASE: (0, 180),
    SHOULDER: (0, 180),
    ELBOW: (0, 180),
    WRIST: (0, 180),
    GRIPPER: (0, 180),
    CAM_BASE: (10, 170)   # SG90 safe range
}

STEP = 2
DELAY = 0.03
RECORD_INTERVAL = 0.05   # seconds

motion = []  # store steps

def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch

def move(ch, delta):
    lo, hi = LIMITS[ch]
    angles[ch] = max(lo, min(hi, angles[ch] + delta))
    kit.servo[ch].angle = angles[ch]

print("🤖 MANUAL RECORD MODE")
print("🔌 POWER ON SERVOS, THEN PRESS ENTER")
input()

kit = ServoKit(channels=16)

kit.servo[BASE].set_pulse_width_range(450, 2550)

for ch, ang in angles.items():
    kit.servo[ch].angle = ang
    time.sleep(0.2)

print("🎥 Recording started")
print("""Controls:
ARM: a/d (Base), w/s (Shoulder), e/r (Elbow), t/g (Wrist), o/c (Gripper)
CAMERA: j/l (Camera Base)
q to stop & save
""")

last_record = time.time()

try:
    while True:
        key = get_key()

        if key == 'a': move(BASE, STEP)
        elif key == 'd': move(BASE, -STEP)
        elif key == 'w': move(SHOULDER, STEP)
        elif key == 's': move(SHOULDER, -STEP)
        elif key == 'e': move(ELBOW, STEP)
        elif key == 'r': move(ELBOW, -STEP)
        elif key == 't': move(WRIST, STEP)
        elif key == 'g': move(WRIST, -STEP)
        elif key == 'o': move(GRIPPER, STEP)
        elif key == 'c': move(GRIPPER, -STEP)
        
        # CAMERA BASE
        elif key == 'j': move(CAM_BASE, -STEP)
        elif key == 'l': move(CAM_BASE, STEP)
        
        elif key == 'q':
            break

        print(
            f"\rB:{angles[BASE]:3d} "
            f"S:{angles[SHOULDER]:3d} "
            f"E:{angles[ELBOW]:3d} "
            f"W:{angles[WRIST]:3d} "
            f"G:{angles[GRIPPER]:3d} "
            f"CB:{angles[CAM_BASE]:3d} ",
            end=""
        )

        now = time.time()
        if now - last_record >= RECORD_INTERVAL:
            motion.append({
                "time": now,
                "angles": angles.copy()
            })
            last_record = now

        time.sleep(DELAY)

except KeyboardInterrupt:
    pass

# Save motion
with open("motions/give_biscuit1.json", "w") as f:
    json.dump(motion, f, indent=2)

print("✅ Motion saved as give_biscuit.json")
