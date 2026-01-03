#!/usr/bin/env python3
from adafruit_servokit import ServoKit
import time

kit = ServoKit(channels=16, address=0x40)

TEST_SERVO = 1

# Disable all channels first
for ch in range(16):
    kit.servo[ch].angle = None

# Configure servo carefully
servo = kit.servo[TEST_SERVO]
servo.set_pulse_width_range(1000, 2000)
servo.actuation_range = 180

print("Waiting before enabling servo...")
time.sleep(2)

# Enable gently
servo.angle = 0
time.sleep(1)

print("Smooth motion starting")

while True:
    for angle in range(0, 91):
        servo.angle = angle
        time.sleep(0.05)
    time.sleep(1)

    for angle in range(90, -1, -1):
        servo.angle = angle
        time.sleep(0.05)
    time.sleep(1)
