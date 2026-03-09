import time
import json
from adafruit_servokit import ServoKit

BASE, SHOULDER, ELBOW, WRIST, GRIPPER = 0, 1, 2, 3, 4
CAM_BASE = 5   # Camera servo

print("🤖 AUTO REPLAY MODE")
print("🔌 POWER ON SERVOS, THEN PRESS ENTER")
input()

kit = ServoKit(channels=16)

# Configure BASE servo pulse width range (same as record mode)
kit.servo[BASE].set_pulse_width_range(450, 2550)

with open("motions/give_biscuit3.json", "r") as f:
    motion = json.load(f)

start_time = motion[0]["time"]

for step in motion:
    angles = step["angles"]

    for ch, ang in angles.items():
        kit.servo[int(ch)].angle = ang

    time.sleep(0.05)  # smooth replay

print("✅ Biscuit delivery completed")
