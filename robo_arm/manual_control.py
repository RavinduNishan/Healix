import sys
import time
import tty
import termios
from adafruit_servokit import ServoKit

# =============================
# SERVO CONFIG
# =============================
BASE, SHOULDER, ELBOW, WRIST, GRIPPER = 0, 1, 2, 3, 4

angles = {
    BASE: 130,
    SHOULDER: 145,
    ELBOW: 180,
    WRIST: 124,
    GRIPPER: 0
}

LIMITS = {
    BASE: (0, 180),
    SHOULDER: (0, 180),
    ELBOW: (0, 180),
    WRIST: (0, 180),
    GRIPPER: (0, 180)
}

STEP = 2        # degrees per step
DELAY = 0.03    # speed (lower = faster)

# =============================
# RAW KEY READER (NON-BLOCKING)
# =============================
def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch

# =============================
# MOVE FUNCTION
# =============================
def move(ch, delta):
    lo, hi = LIMITS[ch]
    angles[ch] = max(lo, min(hi, angles[ch] + delta))
    kit.servo[ch].angle = angles[ch]

# =============================
# START
# =============================
print("🤖 MANUAL HOLD CONTROL (SSH SAFE)")
print("🔌 POWER ON SERVOS, THEN PRESS ENTER")
input()

kit = ServoKit(channels=16)

# Initialize HOME safely
for ch, ang in angles.items():
    kit.servo[ch].angle = ang
    time.sleep(0.2)

print("""
Controls (HOLD KEYS):
a/d : Base
w/s : Shoulder
e/r : Elbow
t/g : Wrist
o/c : Gripper
q   : Quit
""")

# =============================
# MAIN LOOP
# =============================
try:
    while True:
        key = get_key()

        if key == 'a': move(BASE, -STEP)
        elif key == 'd': move(BASE, STEP)

        elif key == 'w': move(SHOULDER, STEP)
        elif key == 's': move(SHOULDER, -STEP)

        elif key == 'e': move(ELBOW, STEP)
        elif key == 'r': move(ELBOW, -STEP)

        elif key == 't': move(WRIST, STEP)
        elif key == 'g': move(WRIST, -STEP)

        elif key == 'o': move(GRIPPER, -STEP)
        elif key == 'c': move(GRIPPER, STEP)

        elif key == 'q':
            print("❌ Exit")
            break

        print(
            f"\rB:{angles[BASE]:3d} "
            f"S:{angles[SHOULDER]:3d} "
            f"E:{angles[ELBOW]:3d} "
            f"W:{angles[WRIST]:3d} "
            f"G:{angles[GRIPPER]:3d} ",
            end=""
        )

        time.sleep(DELAY)

except KeyboardInterrupt:
    pass
