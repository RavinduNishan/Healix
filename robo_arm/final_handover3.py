#!/usr/bin/env python3
"""
Integrated Biscuit Handover System (Version 3)
================================================
This script combines the hand detection logic from hand_test.py with the
motion control from smart_biscuit_handover.py into a single, robust file.

This version is configured to use "give_biscuit1.json".

Flow:
1.  Initialize camera and MediaPipe with settings from hand_test.py.
2.  Move the robot to the pre-defined handover position.
3.  PAUSE and wait for a hand to be detected and held stable.
    - Uses the same detection method as hand_test.py.
4.  If a stable hand is found, complete the handover motion.
5.  If no hand is found within the timeout, run the 'not_hand_detect' motion.
"""

import cv2
import mediapipe as mp
import time
import json
from adafruit_servokit import ServoKit
from picamera2 import Picamera2
import board
import busio
import adafruit_vl53l0x

# ========== CONFIGURATION ==========
# Hand Detection settings from hand_test.py
DETECTION_CONFIDENCE = 0.5
TRACKING_CONFIDENCE = 0.5
MAX_HANDS = 2
SHOW_CAMERA_WINDOW = True

# Handover settings
HAND_WAIT_TIMEOUT = 60      # Maximum wait time for hand (seconds)
HAND_STABLE_DURATION = 4    # How long hand must stay steady (seconds)
STEP_DELAY = 0.05           # Delay between motion steps
DISTANCE_MIN_MM = 80        # Minimum distance for handover (mm)
DISTANCE_MAX_MM = 250       # Maximum distance for handover (mm)

# Exact position to pause for hand detection
HANDOVER_POSITION = {
    '0': 158,   # Base
    '1': 77,    # Shoulder
    '2': 136,   # Channel 2
    '3': 124,   # Channel 3
    '4': 0,     # Gripper (closed, holding biscuit)
    '5': 27     # Camera
}
# ====================================

# Servo channels
BASE, SHOULDER, ELBOW, WRIST_VERTICAL, WRIST_ROTATION, CAM_BASE = 0, 1, 2, 3, 4, 5

# Motion file paths
MOTION_FILE = "motions/give_biscuit1.json"
NOT_HAND_DETECT_FILE = "motions/not_hand_detect.json"

# --- Initialize Hardware and Libraries ---

# Initialize servo kit
print("⚙️  Initializing servo kit...")
kit = ServoKit(channels=16)
kit.servo[BASE].set_pulse_width_range(450, 2550)
print("✅ Servo kit initialized.")

# Initialize VL53L0X sensor
print("🛰️  Initializing VL53L0X sensor...")
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    vl53 = adafruit_vl53l0x.VL53L0X(i2c)
    print("✅ VL53L0X sensor initialized.")
except Exception as e:
    print(f"❌ Failed to initialize VL53L0X sensor: {e}")
    exit(1)

# Initialize MediaPipe Hands
print("🖐️ Initializing MediaPipe Hands...")
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=MAX_HANDS,
    min_detection_confidence=DETECTION_CONFIDENCE,
    min_tracking_confidence=TRACKING_CONFIDENCE
)
print("✅ MediaPipe Hands initialized.")

# Initialize camera
print("📷 Initializing camera...")
try:
    picam2 = Picamera2()
    full_resolution = picam2.sensor_resolution
    picam2.set_controls({"ScalerCrop": (0, 0, full_resolution[0], full_resolution[1])})
    picam2.preview_configuration.main.size = (640, 480)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.configure("preview")
    picam2.start()
    time.sleep(2.0)
    print("✅ Camera initialized successfully.")
except Exception as e:
    print(f"❌ Failed to initialize camera: {e}")
    exit(1)

# --- Core Functions ---

def detect_hand(frame):
    """
    Processes a single frame to detect hands, using logic from hand_test.py.
    Returns:
        - hand_found (bool): True if any hands are detected.
        - processed_frame (np.array): The frame with landmarks drawn on it.
    """
    # Flip for intuitive view and convert color for MediaPipe
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the frame
    results = hands.process(rgb_frame)
    
    hand_found = False
    if results.multi_hand_landmarks:
        hand_found = True
        if SHOW_CAMERA_WINDOW:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )
    return hand_found, frame

def wait_for_stable_hand(timeout, stable_duration):
    """
    Waits for a hand to be detected at the correct distance and held stable.
    """
    print(f"👋 Looking for a hand... (Timeout: {timeout}s, Stability: {stable_duration}s)")
    start_time = time.time()
    stable_start_time = None
    
    while time.time() - start_time < timeout:
        frame = picam2.capture_array()
        if frame is None:
            continue
        
        # Check distance first
        distance = vl53.range
        distance_ok = DISTANCE_MIN_MM <= distance <= DISTANCE_MAX_MM
        
        hand_found, processed_frame = detect_hand(frame)
        
        status_text = f"Dist: {distance}mm"
        
        if distance_ok and hand_found:
            if stable_start_time is None:
                # Start the stability timer
                stable_start_time = time.time()
                print("✋ Hand detected in range! Checking for stability...")
            
            elapsed_stable_time = time.time() - stable_start_time
            
            if elapsed_stable_time >= stable_duration:
                print(f"🎉 Hand stable for {stable_duration} seconds! Proceeding.")
                if SHOW_CAMERA_WINDOW:
                    cv2.destroyAllWindows()
                return True
            else:
                # Show countdown
                remaining = stable_duration - elapsed_stable_time
                status_text += f" | HOLD: {remaining:.1f}s"
        else:
            # Condition not met, reset stability timer
            if stable_start_time is not None:
                print("⚠️  Hand lost or out of range. Resetting stability timer.")
            stable_start_time = None
            if not distance_ok:
                status_text += " | Too close/far"
            if not hand_found:
                status_text += " | No Hand"

        if SHOW_CAMERA_WINDOW:
            dist_color = (0, 255, 0) if distance_ok else (0, 0, 255)
            cv2.putText(processed_frame, f"Distance: {distance}mm (Safe: {distance_ok})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, dist_color, 2)
            
            palm_color = (0, 255, 0) if hand_found else (0, 0, 255)
            cv2.putText(processed_frame, f"Open Palm: {hand_found}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, palm_color, 2)
            
            hold_ok = stable_start_time and (time.time() - stable_start_time) >= stable_duration
            hold_color = (0, 255, 0) if hold_ok else ((0, 255, 255) if stable_start_time else (0, 0, 255))
            if stable_start_time:
                remaining = max(0.0, stable_duration - (time.time() - stable_start_time))
                hold_text = f"Hold Time OK: {hold_ok} ({remaining:.1f}s left)"
            else:
                hold_text = f"Hold Time OK: False (Waiting for palm & safe dist)"
            cv2.putText(processed_frame, hold_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, hold_color, 2)

            cv2.imshow("Hand Detection", processed_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("❌ User cancelled.")
                return False
                
    print("⏱️  Timeout reached. No stable hand was detected in the correct range.")
    return False

def play_motion(motion_data, start_step=0, end_step=None):
    """Plays a segment of a motion file."""
    if end_step is None:
        end_step = len(motion_data) - 1
        
    print(f"🤖 Playing motion steps {start_step} to {end_step}...")
    for i in range(start_step, end_step + 1):
        step = motion_data[i]
        for channel_str, angle in step['angles'].items():
            kit.servo[int(channel_str)].angle = angle
        time.sleep(STEP_DELAY)

def play_motion_from_file(filepath):
    """Loads and plays an entire motion file."""
    print(f"📁 Loading and playing motion from {filepath}...")
    with open(filepath, 'r') as f:
        motion_data = json.load(f)
    play_motion(motion_data)

# --- Main Execution ---

def main():
    """Main program logic."""
    print("\n" + "=" * 70)
    print("🤖 INTEGRATED BISCUIT HANDOVER SYSTEM (v3)")
    print("=" * 70)

    # 1. Load motion data
    try:
        with open(MOTION_FILE, 'r') as f:
            motion = json.load(f)
        print(f"✅ Loaded {len(motion)} motion steps from {MOTION_FILE}")
    except FileNotFoundError:
        print(f"❌ ERROR: Motion file not found at {MOTION_FILE}")
        return

    # 2. Find the handover pause position in the motion data
    handover_pause_idx = -1
    for i, step in enumerate(motion):
        if all(step['angles'].get(ch) == HANDOVER_POSITION[ch] for ch in HANDOVER_POSITION.keys()):
            handover_pause_idx = i
            break
            
    if handover_pause_idx == -1:
        print("❌ ERROR: Could not find the exact HANDOVER_POSITION in the motion file.")
        return
    print(f"✅ Handover position found at step {handover_pause_idx}.")

    # 3. Move robot to handover position
    play_motion(motion, 0, handover_pause_idx)
    print("✅ Robot is at the handover position. Awaiting hand...")

    # 4. Wait for a stable hand
    hand_is_ready = wait_for_stable_hand(HAND_WAIT_TIMEOUT, HAND_STABLE_DURATION)

    # 5. Complete or cancel the handover
    if hand_is_ready:
        print("✅ Completing handover...")
        play_motion(motion, handover_pause_idx + 1)
        print("🎉 HANDOVER COMPLETE!")
    else:
        print("⚠️ No hand detected. Returning biscuit...")
        play_motion_from_file(NOT_HAND_DETECT_FILE)
        print("🔙 HANDOVER CANCELLED.")

if __name__ == "__main__":
    try:
        main()
    finally:
        # Cleanup
        print("\n🧹 Cleaning up resources...")
        picam2.stop()
        hands.close()
        cv2.destroyAllWindows()
        print("✅ Program finished.")
