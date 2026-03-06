#!/usr/bin/env python3
"""
Minimal camera test - just verify if camera can capture frames
"""
import time
from picamera2 import Picamera2

print("=" * 60)
print("MINIMAL CAMERA TEST")
print("=" * 60)

try:
    print("\n[1/4] Creating Picamera2 object...")
    picam2 = Picamera2()
    print("     ✅ Picamera2 object created")
    
    print("\n[2/4] Configuring camera...")
    picam2.preview_configuration.main.size = (640, 480)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.configure("preview")
    print("     ✅ Camera configured")
    
    print("\n[3/4] Starting camera...")
    picam2.start()
    print("     ✅ Camera started")
    
    print("\n[4/4] Waiting 2 seconds for warm-up...")
    time.sleep(2)
    print("     ✅ Warm-up complete")
    
    print("\n📷 Attempting to capture 5 test frames...")
    for i in range(5):
        frame = picam2.capture_array()
        print(f"     Frame {i+1}: shape={frame.shape}, dtype={frame.dtype}, min={frame.min()}, max={frame.max()}")
        time.sleep(0.5)
    
    print("\n✅ SUCCESS! Camera is working correctly!")
    print(f"   Camera is capturing {frame.shape[1]}x{frame.shape[0]} RGB images")
    
    picam2.stop()
    print("   Camera stopped cleanly")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\n⚠️  Camera test FAILED")
    print("   Check if camera is enabled: 'sudo raspi-config' > Interface Options > Camera")

print("\n" + "=" * 60)
