#!/usr/bin/env python3
"""
Camera + Hand Detection Test with Image Saving
No display window needed - saves images to disk
"""
import time
from picamera2 import Picamera2
import cv2
import mediapipe as mp
import os

print("=" * 60)
print("CAMERA + HAND DETECTION TEST (with image saving)")
print("=" * 60)

# Create output directory
output_dir = "camera_test_output"
os.makedirs(output_dir, exist_ok=True)
print(f"📁 Saving images to: {output_dir}/")

try:
    # MediaPipe setup
    print("\n[1/5] Initializing MediaPipe...")
    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )
    print("     ✅ MediaPipe initialized")
    
    # Camera setup
    print("\n[2/5] Starting camera...")
    picam2 = Picamera2()
    picam2.preview_configuration.main.size = (640, 480)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.configure("preview")
    picam2.start()
    time.sleep(2)
    print("     ✅ Camera started and warmed up")
    
    # Detection function
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
    
    print("\n[3/5] Testing frame capture...")
    test_frame = picam2.capture_array()
    print(f"     ✅ Captured frame: {test_frame.shape}")
    cv2.imwrite(f"{output_dir}/test_frame.jpg", cv2.cvtColor(test_frame, cv2.COLOR_RGB2BGR))
    print(f"     💾 Saved: {output_dir}/test_frame.jpg")
    
    print("\n[4/5] Running hand detection for 15 seconds...")
    print("     👋 Hold your horizontal palm in front of the camera!")
    print()
    
    start_time = time.time()
    frame_count = 0
    hand_detected_count = 0
    valid_hand_count = 0
    last_save = 0
    
    while time.time() - start_time < 15:
        frame = picam2.capture_array()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)
        
        frame_count += 1
        elapsed = time.time() - start_time
        
        status = "❌ No hand"
        color = (0, 0, 255)  # Red
        
        if results.multi_hand_landmarks:
            hand_detected_count += 1
            for lm in results.multi_hand_landmarks:
                # Draw hand landmarks on frame
                mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)
                
                if fingers_horizontal_extended(lm):
                    valid_hand_count += 1
                    status = "✅ VALID HORIZONTAL PALM!"
                    color = (0, 255, 0)  # Green
                    print(f"     [{elapsed:.1f}s] {status}")
                    
                    # Save image every 2 seconds when valid hand detected
                    if elapsed - last_save >= 2:
                        filename = f"{output_dir}/valid_hand_{int(elapsed)}.jpg"
                        cv2.imwrite(filename, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                        print(f"     💾 Saved: {filename}")
                        last_save = elapsed
                else:
                    status = "⚠️  Hand detected but not horizontal"
                    color = (255, 165, 0)  # Orange
        
        # Add status text to frame
        cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(frame, f"Time: {elapsed:.1f}s", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        time.sleep(0.2)
    
    # Save final frame
    cv2.imwrite(f"{output_dir}/final_frame.jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    
    print(f"\n[5/5] Test complete!")
    print(f"\n📊 Results:")
    print(f"   Total frames: {frame_count}")
    print(f"   Frames with hand detected: {hand_detected_count}")
    print(f"   Frames with VALID horizontal palm: {valid_hand_count}")
    print(f"   Detection rate: {valid_hand_count/frame_count*100:.1f}%")
    print(f"\n📁 Check images in: {output_dir}/")
    
    if valid_hand_count > 0:
        print("\n✅ SUCCESS! Camera and hand detection working!")
    else:
        print("\n⚠️  No valid hand detected. Check saved images and try again.")
    
    picam2.stop()
    hands.close()
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
