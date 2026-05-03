import sys
import time
import tty
import termios
from adafruit_servokit import ServoKit

# =============================
# SERVO CHANNEL CONFIG
# =============================
BASE, SHOULDER, ELBOW, WRIST, GRIPPER = 0, 1, 2, 3, 4
CAM_BASE = 5   # Only camera servo now

# =============================
# INITIAL ANGLES
# =============================
angles = {
    BASE: 90,
    SHOULDER: 147,
    ELBOW: 180,
    WRIST: 124,
    GRIPPER: 0,
    CAM_BASE: 83
}

# =============================
# SAFE LIMITS
# =============================
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

# =============================
# RAW KEY READER
# =============================
def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# =============================
# MOVE FUNCTION
# =============================
def move(channel, delta):
    low, high = LIMITS[channel]
    angles[channel] = max(low, min(high, angles[channel] + delta))
    kit.servo[channel].angle = angles[channel]

# =============================
# START PROGRAM
# =============================
print("🤖 ARM + CAMERA BASE CONTROL")
print("🔌 POWER ON SERVOS, THEN PRESS ENTER")
input()

kit = ServoKit(channels=16)

kit.servo[BASE].set_pulse_width_range(450, 2550)

# Initialize all servos
for ch, ang in angles.items():
    kit.servo[ch].angle = ang
    time.sleep(0.15)

print("""
================ CONTROLS ================

ARM:
a/d : Base
w/s : Shoulder
e/r : Elbow
t/g : Wrist
o/c : Gripper

CAMERA:
j/l : Camera Base (left/right)

q   : Quit

==========================================
""")

# =============================
# MAIN LOOP
# =============================
try:
    while True:
        key = get_key()

        # ARM
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
            print("\n❌ Exiting...")
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

        time.sleep(DELAY)

except KeyboardInterrupt:
    print("\n⚠ Interrupted safely")