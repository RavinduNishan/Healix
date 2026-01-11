import time
from adafruit_servokit import ServoKit

# =============================
# CONFIG
# =============================
BASE_CH = 0        # Base servo channel
MIN_ANGLE = 30     # safe minimum
MAX_ANGLE = 150    # safe maximum
STEP = 2           # degrees per step
DELAY = 0.05       # slow movement

# =============================
# START
# =============================
print("🤖 BASE SERVO TEST")
print("🔌 POWER ON SERVOS NOW")
input("➡ Press ENTER to start base test...")

kit = ServoKit(channels=16)

# Move to center first (safe)
center_angle = 90
kit.servo[BASE_CH].angle = center_angle
print(f"➡ Moving to center: {center_angle}°")
time.sleep(2)

# =============================
# SWEEP LEFT
# =============================
print("⬅ Sweeping LEFT")
for angle in range(center_angle, MIN_ANGLE, -STEP):
    kit.servo[BASE_CH].angle = angle
    print(f"Base angle: {angle}°")
    time.sleep(DELAY)

time.sleep(1)

# =============================
# SWEEP RIGHT
# =============================
print("➡ Sweeping RIGHT")
for angle in range(MIN_ANGLE, MAX_ANGLE, STEP):
    kit.servo[BASE_CH].angle = angle
    print(f"Base angle: {angle}°")
    time.sleep(DELAY)

time.sleep(1)

# =============================
# RETURN TO CENTER
# =============================
print("🔄 Returning to center")
for angle in range(MAX_ANGLE, center_angle, -STEP):
    kit.servo[BASE_CH].angle = angle
    print(f"Base angle: {angle}°")
    time.sleep(DELAY)

print("✅ BASE SERVO TEST COMPLETE")
