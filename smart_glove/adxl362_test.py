import spidev
import time

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0, 0)  # bus 0, CE0
spi.max_speed_hz = 1000000
spi.mode = 0

# Write register
def write_register(reg, value):
    spi.xfer2([0x0A, reg, value])

# Read XYZ data
def read_xyz():
    data = spi.xfer2([0x0B, 0x0E, 0, 0, 0, 0, 0, 0])

    x = data[2] | (data[3] << 8)
    y = data[4] | (data[5] << 8)
    z = data[6] | (data[7] << 8)

    # convert signed values
    if x > 32767: x -= 65536
    if y > 32767: y -= 65536
    if z > 32767: z -= 65536

    return x, y, z

# Enable measurement mode
write_register(0x2D, 0x02)

print("ADXL362 Test Started")

while True:
    x, y, z = read_xyz()

    print(f"X: {x}  Y: {y}  Z: {z}")

    time.sleep(0.5)