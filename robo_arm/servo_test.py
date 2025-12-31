#!/usr/bin/env python3
from adafruit_servokit import ServoKit
import time

kit = ServoKit(channels=16)

SERVO_CH = 3       # 4th servo
START_ANGLE = 0
END_ANGLE = 45
STEP = 1           # 1 degree step (smaller = slower)
DELAY = 0.05       # increase this to make it EVEN slower

# Turn OFF all other channels
for ch in range(16):
    if ch != SERVO_CH:
        kit.servo[ch].angle = None

# Set safe pulse width for MG996R
kit.servo[SERVO_CH].set_pulse_width_range(500, 2500)

print("Only 4th servo is moving VERY SLOWLY")

try:
    while True:
        # Move forward slowly
        for angle in range(START_ANGLE, END_ANGLE + 1, STEP):
            kit.servo[SERVO_CH].angle = angle
            time.sleep(DELAY)

        time.sleep(1)

        # Move backward slowly
        for angle in range(END_ANGLE, START_ANGLE - 1, -STEP):
            kit.servo[SERVO_CH].angle = angle
            time.sleep(DELAY)

        time.sleep(1)

except KeyboardInterrupt:
    kit.servo[SERVO_CH].angle = None
    print("\nStopped safely")
