from picamera2 import Picamera2
import cv2
import mediapipe as mp
import time

# MediaPipe setup - SAME AS horizontal_palm_test.py
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Camera setup
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

print("🔍 Hand Detection Test (No Display Mode)")
print("=" * 50)
print("Hold your palm horizontally and watch the console")
print("Press Ctrl+C to exit")
print("=" * 50)

def fingers_horizontal_extended(lm):
    """Check if fingers are extended horizontally - SAME AS horizontal_palm_test.py"""
    tips = [8, 12, 16, 20]
    
    ys = [lm.landmark[i].y for i in tips]
    y_diff = max(ys) - min(ys)
    
    xs = [lm.landmark[i].x for i in tips]
    x_spread = max(xs) - min(xs)
    
    horizontal = y_diff <= 0.1
    extended = x_spread >= 0.15
    
    return horizontal, extended, y_diff, x_spread

try:
    last_status = None
    detection_start = None
    
    while True:
        frame = picam2.capture_array()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)
        
        status = "❌ No hand detected"
        
        if results.multi_hand_landmarks:
            for lm in results.multi_hand_landmarks:
                horizontal, extended, y_diff, x_spread = fingers_horizontal_extended(lm)
                
                if horizontal and extended:
                    status = "✅ VALID HAND - Ready for biscuit!"
                    if detection_start is None:
                        detection_start = time.time()
                    else:
                        duration = time.time() - detection_start
                        status += f" ({duration:.1f}s)"
                else:
                    detection_start = None
                    reasons = []
                    if not horizontal:
                        reasons.append(f"fingers not horizontal (y_diff={y_diff:.3f})")
                    if not extended:
                        reasons.append(f"fingers not extended (x_spread={x_spread:.3f})")
                    status = f"⚠️  Hand detected but: {', '.join(reasons)}"
        else:
            detection_start = None
        
        # Only print when status changes or every 2 seconds
        if status != last_status or (detection_start and int(time.time() - detection_start) % 2 == 0):
            print(status)
            last_status = status
        
        time.sleep(0.2)

except KeyboardInterrupt:
    print("\n\n✅ Test completed")
    picam2.stop()
    hands.close()
