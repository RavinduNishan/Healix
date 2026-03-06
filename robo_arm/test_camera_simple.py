#!/usr/bin/env python3
"""
Simple camera test - same initialization as smart_biscuit_handover.py
"""
import time
from picamera2 import Picamera2
import cv2
import mediapipe as mp

print("🔧 Testing camera initialization (same as smart_biscuit_handover.py)")
print("=" * 60)

# EXACT same setup as smart_biscuit_handover.py
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

print("📷 Camera started - warming up...")
time.sleep(2)

# Test capture
try:
    test_frame = picam2.capture_array()
    print(f"✅ Camera test OK - capturing {test_frame.shape}")
except Exception as e:
    print(f"❌ Camera test failed: {e}")
    exit(1)

print("\n🎬 Starting hand detection test (10 seconds)...")
print("👋 Hold your hand with horizontal palm in front of camera\n")

# Same detection logic as smart_biscuit_handover.py
def fingers_horizontal_extended(lm):
    tips = [8, 12, 16, 20]
    ys = [lm.landmark[i].y for i in tips]
    y_diff = max(ys) - min(ys)
    if y_diff > 0.1:
        return False
    xs = [lm.landmark[i].x for i in tips]
    x_spread = max(xs) - min(xs)
    if x_spread < 0.15:
        return False
    return True

hand_detected_count = 0
frame_count = 0
start = time.time()

while time.time() - start < 10:
    try:
        frame = picam2.capture_array()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)
        
        frame_count += 1
        
        if results.multi_hand_landmarks:
            for lm in results.multi_hand_landmarks:
                if fingers_horizontal_extended(lm):
                    hand_detected_count += 1
                    print(f"✅ VALID HAND DETECTED! (frame {frame_count})")
                else:
                    print(f"⚠️  Hand seen but not horizontal (frame {frame_count})")
        
        time.sleep(0.15)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        break

print(f"\n📊 Results:")
print(f"   Total frames: {frame_count}")
print(f"   Valid hand detections: {hand_detected_count}")
print(f"   Detection rate: {hand_detected_count/frame_count*100:.1f}%")

if hand_detected_count > 0:
    print("\n✅ Camera and hand detection working correctly!")
else:
    print("\n⚠️  No valid hand detected. Try holding palm horizontally.")

picam2.stop()
hands.close()
print("\n✅ Test complete")
