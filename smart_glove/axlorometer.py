import spidev
import time

# Setup SPI
spi = spidev.SpiDev()
spi.open(0, 0) # Open bus 0, device (CS) 0
spi.max_speed_hz = 1000000
spi.mode = 0b00

def read_adxl362_reg(reg):
    # ADXL362 Read Command is 0x0B
    response = spi.xfer2([0x0B, reg, 0x00])
    return response[2]

def get_data():
    # Read X, Y (low and high bytes)
    x_low = read_adxl362_reg(0x0E)
    x_high = read_adxl362_reg(0x0F)
    y_low = read_adxl362_reg(0x10)
    y_high = read_adxl362_reg(0x11)
    
    # Read Temperature (low and high bytes)
    t_low = read_adxl362_reg(0x14)
    t_high = read_adxl362_reg(0x15)

    # Convert to 12-bit signed integers
    x = (x_high << 8) | x_low
    y = (y_high << 8) | y_low
    temp = (t_high << 8) | t_low
    
    return x, y, temp

# Initialize: Set to Measurement Mode (Reg 0x2D, write 0x02)
spi.xfer2([0x0A, 0x2D, 0x02])

try:
    while True:
        x, y, t = get_data()
        # Temp conversion (rough estimate for ADXL362)
        celsius = (t - 185) / 10.0 
        
        print(f"X: {x} | Y: {y} | Temp: {celsius:.2f}°C")
        time.sleep(0.5)
except KeyboardInterrupt:
    spi.close()