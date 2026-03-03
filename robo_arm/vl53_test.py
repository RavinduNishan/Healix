import time
import board
import busio
import adafruit_vl53l0x

print("Initializing I2C...")
i2c = busio.I2C(board.SCL, board.SDA)

print("Initializing VL53L0X...")
sensor = adafruit_vl53l0x.VL53L0X(i2c)

print("VL53L0X Ready!")
print("----------------------")

while True:
    distance = sensor.range  # distance in mm
    print(f"Distance: {distance} mm")
    time.sleep(0.5)