#!/usr/bin/env python3
"""
Smart Biscuit Handover System
==============================
Integrates motion replay with hand detection for safe biscuit handover.

Flow:
1. Load recorded motion from give_biscuit1.json
2. Play motion until handover position (all 6 channels match exact position)
3. PAUSE and detect horizontal palm hand gesture
4. Wait for hand to remain stable for 5 seconds
5. If hand detected: Complete handover motion
6. If no hand (60s timeout): Return biscuit to original position
"""

import cv2
import mediapipe as mp
import time
import json
from adafruit_servokit import ServoKit
from picamera2 import Picamera2

# ========== CONFIGURATION ==========
# Adjust these values if needed
HAND_WAIT_TIMEOUT = 60        # Maximum wait time for hand (seconds)
HAND_STABLE_DURATION = 5      # How long hand must stay steady (seconds)
HAND_DETECTION_CONFIDENCE = 0.7  # Same as horizontal_palm_test.py
HAND_TRACKING_CONFIDENCE = 0.7   # Same as horizontal_palm_test.py
SHOW_CAMERA_WINDOW = True     # Show camera feed during detection (VNC only)
STEP_DELAY = 0.05             # Delay between motion steps (seconds) - increase to slow down

# Exact position to pause for hand detection (all 6 channels must match)
HANDOVER_POSITION = {
    '0': 158,   # Base
    '1': 77,   # Shoulder
    '2': 136,   # Channel 2
    '3': 124,   # Channel 3
    '4': 0,     # Gripper (closed, holding biscuit)
    '5': 27     # Camera
}
# ====================================

# Servo channels
BASE = 0
SHOULDER = 1
ELBOW = 2
WRIST_VERTICAL = 3
WRIST_ROTATION = 4
CAM_BASE = 5

# Initialize servo kit
kit = ServoKit(channels=16)

# Set actuation range for base servo (custom pulse width)
kit.servo[BASE].set_pulse_width_range(450, 2550)

# Motion file path
MOTION_FILE = "motions/give_biscuit1.json"
NOT_HAND_DETECT_FILE = "motions/not_hand_detect.json"

# Initialize MediaPipe Hands (same parameters as horizontal_palm_test.py)
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=HAND_DETECTION_CONFIDENCE,
    min_tracking_confidence=HAND_TRACKING_CONFIDENCE
)

# Initialize camera (same setup as horizontal_palm_test.py)
print("📷 Initializing camera...")
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()
time.sleep(2)  # Camera warm-up

# Test camera
print("📸 Testing camera capture...")
test_frame = picam2.capture_array()
if test_frame is None or test_frame.size == 0:
    print("❌ Camera test failed!")
    exit(1)
print(f"✅ Camera working - Frame size: {test_frame.shape}")


def fingers_horizontal_extended(hand_landmarks):
    """
    Check if fingers are in horizontal position with palm facing camera.
    Same logic as horizontal_palm_test.py
    """
    finger_tips = [
        hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP],
        hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP],
        hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP],
        hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    ]
    
    finger_mcp = [
        hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP],
        hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP],
        hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP],
        hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
    ]
    
    # Check vertical alignment (y-coordinates should be similar for horizontal orientation)
    y_coords = [tip.y for tip in finger_tips]
    y_diff = max(y_coords) - min(y_coords)
    
    # Check horizontal spread (x-coordinates should be spread out)
    x_coords = [tip.x for tip in finger_tips]
    x_spread = max(x_coords) - min(x_coords)
    
    # Same thresholds as horizontal_palm_test.py
    if y_diff <= 0.1 and x_spread >= 0.15:
        return True
    
    return False


def check_hand_ready():
    """
    Capture frame and check if hand is in correct position.
    Returns: (is_ready: bool, frame: np.array, hand_detected: bool)
    """
    frame = picam2.capture_array()
    if frame is None:
        return False, None, False
    
    # Convert BGR to RGB for MediaPipe (same as horizontal_palm_test.py)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    
    hand_detected = False
    hand_ready = False
    
    if results.multi_hand_landmarks:
        hand_detected = True
        for hand_landmarks in results.multi_hand_landmarks:
            if fingers_horizontal_extended(hand_landmarks):
                hand_ready = True
            
            # Draw hand skeleton on frame
            if SHOW_CAMERA_WINDOW:
                mp_drawing.draw_landmarks(
                    frame, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS
                )
    
    return hand_ready, frame, hand_detected


def wait_for_stable_hand(timeout=60, stable_duration=5, show_display=True):
    """
    Wait for hand to be detected and remain stable.
    
    Args:
        timeout: Maximum time to wait (seconds)
        stable_duration: How long hand must stay stable (seconds)
        show_display: Show camera window with feedback
    
    Returns:
        True if hand detected and stable, False if timeout
    """
    start_time = time.time()
    stable_start = None
    consecutive_detections = 0
    last_status_time = time.time()
    
    print(f"👋 Looking for horizontal palm hand gesture...")
    print(f"   - Hand must be stable for {stable_duration} seconds")
    print(f"   - Timeout after {timeout} seconds")
    
    while True:
        elapsed = time.time() - start_time
        
        # Check timeout
        if elapsed > timeout:
            print(f"\n⏱️  Timeout reached ({timeout}s) - No stable hand detected")
            if show_display:
                cv2.destroyAllWindows()
            return False
        
        # Status update every 10 seconds
        if time.time() - last_status_time >= 10:
            print(f"   ... still looking ({int(elapsed)}s / {timeout}s)")
            last_status_time = time.time()
        
        # Check hand position
        hand_ready, frame, hand_detected = check_hand_ready()
        
        if hand_ready:
            if consecutive_detections == 0:
                print("✋ Hand detected! Checking stability...")
            
            consecutive_detections += 1
            
            # Start stability timer after 3 consecutive detections
            if consecutive_detections >= 3 and stable_start is None:
                stable_start = time.time()
                print("✅ Hand position confirmed - Starting stability timer...")
            
            # Check if stable duration reached
            if stable_start is not None:
                stable_time = time.time() - stable_start
                remaining = stable_duration - stable_time
                
                if remaining <= 0:
                    print(f"🎉 Hand stable for {stable_duration} seconds - Ready for handover!")
                    if show_display:
                        cv2.destroyAllWindows()
                    return True
                
                # Show countdown
                if show_display and frame is not None:
                    cv2.putText(frame, f"HOLD STEADY: {remaining:.1f}s", 
                              (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                              0.7, (0, 255, 0), 2)
        else:
            # Hand lost or not in correct position
            if consecutive_detections > 0:
                # Allow 1 second grace period for brief interruptions
                if stable_start is not None:
                    grace_elapsed = time.time() - stable_start
                    if grace_elapsed < 1.0:
                        # Still in grace period, don't reset
                        if show_display and frame is not None:
                            cv2.putText(frame, "Keep hand steady...", 
                                      (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                                      0.7, (255, 165, 0), 2)
                    else:
                        # Grace period expired, reset
                        print("⚠️  Hand moved or lost - Restarting detection...")
                        consecutive_detections = 0
                        stable_start = None
                else:
                    # Not yet stable, just lost detection
                    consecutive_detections = 0
            
            if show_display and frame is not None:
                if hand_detected:
                    cv2.putText(frame, "Wrong hand position", 
                              (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                              0.7, (0, 0, 255), 2)
                else:
                    cv2.putText(frame, "No hand detected", 
                              (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                              0.7, (0, 0, 255), 2)
        
        # Show frame
        if show_display and frame is not None:
            cv2.imshow("Hand Detection - Biscuit Handover", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n❌ Detection cancelled by user")
                cv2.destroyAllWindows()
                return False
        
        time.sleep(0.1)  # Small delay to reduce CPU usage


def play_motion_segment(start_step, end_step, reverse=False):
    """
    Play a segment of the recorded motion.
    
    Args:
        start_step: Starting step index
        end_step: Ending step index (inclusive)
        reverse: If True, play from end_step to start_step
    """
    if reverse:
        steps = range(end_step, start_step - 1, -1)
        print(f"   Reversing motion: step {end_step} → {start_step}")
    else:
        steps = range(start_step, end_step + 1)
    
    for i in steps:
        step = motion[i]
        angles = step['angles']
        
        # Set all servo positions
        for channel_str, angle in angles.items():
            channel = int(channel_str)
            kit.servo[channel].angle = angle
        
        # Delay between steps (adjust STEP_DELAY to change speed)
        time.sleep(STEP_DELAY)


def play_motion_file(filepath):
    """
    Load and play all steps from a motion JSON file.
    """
    print(f"   Loading motion from: {filepath}")
    with open(filepath, 'r') as f:
        steps = json.load(f)
    print(f"   Playing {len(steps)} steps...")
    for step in steps:
        angles = step['angles']
        for channel_str, angle in angles.items():
            channel = int(channel_str)
            kit.servo[channel].angle = angle
        time.sleep(STEP_DELAY)


# ============================================================
# MAIN EXECUTION
# ============================================================

print("\n" + "=" * 70)
print("🤖 SMART BISCUIT HANDOVER SYSTEM")
print("=" * 70)

# Step 1: Load motion data
print(f"\n📁 Loading motion from: {MOTION_FILE}")
with open(MOTION_FILE, 'r') as f:
    motion = json.load(f)
print(f"✅ Loaded {len(motion)} motion steps")

# Find the exact handover position (all 6 channels must match)
print(f"\n🔍 Searching for handover position:")
print(f"   Target: Base={HANDOVER_POSITION['0']}°, Shoulder={HANDOVER_POSITION['1']}°, "
      f"Ch2={HANDOVER_POSITION['2']}°, Ch3={HANDOVER_POSITION['3']}°, "
      f"Gripper={HANDOVER_POSITION['4']}°, Camera={HANDOVER_POSITION['5']}°")

handover_pause_idx = None
for i, step in enumerate(motion):
    angles = step['angles']
    # Check if ALL 6 channels match
    if all(angles.get(ch) == HANDOVER_POSITION[ch] for ch in HANDOVER_POSITION.keys()):
        handover_pause_idx = i
        print(f"✅ Found handover position at step {i}")
        break

if handover_pause_idx is None:
    print("❌ ERROR: Could not find exact handover position in motion!")
    print("   Please verify the HANDOVER_POSITION values match an entry in give_biscuit.json")
    exit(1)

# Step 2: Play motion up to handover position
print("\n🤖 Moving to handover position...")
print(f"   Playing steps 0 → {handover_pause_idx}")
play_motion_segment(0, handover_pause_idx)
print(f"✅ Robot at handover position - Step {handover_pause_idx}")
print(f"   All servos at exact position:")
for ch, angle in HANDOVER_POSITION.items():
    print(f"   - Channel {ch}: {angle}°")

# Step 3: Wait for hand detection (BEFORE continuing motion)
print("\n" + "=" * 70)
print("⏸️  PAUSED - Waiting for hand to receive biscuit...")
print("=" * 70)
hand_ready = wait_for_stable_hand(
    timeout=HAND_WAIT_TIMEOUT, 
    stable_duration=HAND_STABLE_DURATION, 
    show_display=SHOW_CAMERA_WINDOW
)
print("=" * 70)

if hand_ready:
    # Step 4a: Hand detected - Complete handover motion
    print("\n✅ Hand is ready - Completing biscuit handover...")
    print(f"   Playing steps {handover_pause_idx + 1} → {len(motion) - 1}")
    play_motion_segment(handover_pause_idx + 1, len(motion) - 1)
    print("\n✅ HANDOVER COMPLETE - Biscuit released!")
    
else:
    # Step 4b: No hand detected - Run not_hand_detect motion
    print("\n⚠️  No hand detected - Running not_hand_detect motion")
    play_motion_file(NOT_HAND_DETECT_FILE)
    print("\n🔙 HANDOVER CANCELLED - not_hand_detect motion complete")

# Cleanup
print("\n🧹 Cleaning up...")
picam2.stop()
hands.close()
cv2.destroyAllWindows()

print("\n" + "=" * 70)
print("✅ PROGRAM COMPLETE")
print("=" * 70)
