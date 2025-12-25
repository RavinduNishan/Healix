#!/usr/bin/env python3
from adafruit_servokit import ServoKit
import time

# Initialize (address=0x40 is default for PCA9685)
kit = ServoKit(channels=16, address=0x40)

# === DISABLE ALL CHANNELS EXCEPT 4 (servos go limp/no PWM) ===
for ch in range(16):
    if ch != 4:
        kit.servo[ch].angle = None  # No pulse = fully OFF

# Set safe pulse range for MG996R (0°=1ms, 180°=2ms; change for 45° max)
kit.servo[4].set_pulse_width_range(1000, 2000)
# For 0°–45° only: kit.servo[4].set_pulse_width_range(1000, 1250)

print("TEST STARTED → ONLY CHANNEL 4 ACTIVE")
print("All others 100% OFF (limp & silent). Servo on ch4 should sweep...")

try:
    while True:
        print("Channel 4 → 180°")
        kit.servo[4].angle = 180  # Or 45 for limited range
        time.sleep(2)
        print("Channel 4 → 0°")
        kit.servo[4].angle = 0
        time.sleep(2)
except KeyboardInterrupt:
    print("\nStopped by user")
finally:
    # Cleanup: All channels OFF
    for ch in range(16):
        kit.servo[ch].angle = None
    print("All servos OFF")