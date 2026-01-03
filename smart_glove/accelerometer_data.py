import spidev
import time
import json
from firebase_admin import credentials, db, initialize_app

# --- Firebase Setup ---
cred = credentials.Certificate("/home/isuru/Healix/smart_glove/healix-e3ba5-firebase-adminsdk-fbsvc-b50fbbd766.json")
initialize_app(cred, {'databaseURL': 'https://healix-e3ba5-default-rtdb.firebaseio.com/'})
ref = db.reference('patient_data')

# --- ADXL362 Setup ---
spi = spidev.SpiDev()
spi.open(0, 0) 
spi.max_speed_hz = 1000000

def write_reg(reg, val):
    spi.xfer2([0x0A, reg, val])

def read_regs(reg, count):
    # Command 0x0B is "Read Register"
    return spi.xfer2([0x0B, reg] + [0] * count)[2:]

# INITIALIZE: Set to Measurement Mode (Write 0x02 to Reg 0x2D)
write_reg(0x2D, 0x02)
time.sleep(0.1)

def get_data():
    # Read 8 bytes starting from 0x0E (XDATA_L, XDATA_H, YDATA_L, YDATA_H, ZDATA_L, ZDATA_H, TEMP_L, TEMP_H)
    raw = read_regs(0x0E, 8)
    
    # Helper to convert two 8-bit bytes to signed 12-bit
    def to_int(low, high):
        combined = (high << 8) | low
        # Handle sign for 12-bit (ADXL362 default)
        if combined & 0x800:
            combined -= 0x1000
        return combined

    x = to_int(raw[0], raw[1])
    y = to_int(raw[2], raw[3])
    z = to_int(raw[4], raw[5])
    
    # Temperature (Sign extended 12-bit * 0.065 degrees C)
    raw_temp = to_int(raw[6], raw[7])
    temp_c = raw_temp * 0.065

    return {"x": x, "y": y, "z": z, "temp": round(temp_c, 2)}

# --- Main Loop ---
while True:
    try:
        data = get_data()
        data['timestamp'] = time.time()
        
        # Log and Upload
        print(f"Sensor Reading: {data}")
        ref.push(data)
        
    except Exception as e:
        print(f"Error: {e}")
        
    time.sleep(0.5)