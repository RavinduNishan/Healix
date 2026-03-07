# Smart Biscuit Handover System

## Overview
This script performs intelligent biscuit handover with hand detection and safety return features.

## How It Works

### Phase 1: Pick Up Biscuit
- Gripper opens (angle 0)
- Robot moves to biscuit and grips it (gripper closes to ~112)

### Phase 2: Move to Handover Position
- Robot carries biscuit to handover position
- Stops with gripper still closed (holding biscuit securely)

### Phase 3: Wait for Hand Detection (NEW)
- **Camera activates** and looks for horizontal palm gesture
- **Requirements for valid hand:**
  - Palm must be open
  - Fingers extended horizontally (not pointing up or down)
  - Hand must remain stable for **5 seconds**
  
- **If hand detected and stable:**
  - ✅ Gripper opens and releases biscuit
  - ✅ Mission complete!

- **If no hand within 1 minute:**
  - 🔙 Robot carefully returns biscuit to original position
  - 🔙 Motion plays in reverse
  - ✅ Biscuit safely stored

## Usage

```bash
cd /home/isuru/Healix/robo_arm
python3 smart_biscuit_handover.py
```

## Hand Gesture Requirements

**Correct Hand Position:**
- Palm facing the camera
- Fingers straight and horizontal (like offering a handshake)
- Hand steady for 5 seconds

**Wrong Hand Positions (will not trigger):**
- Fingers pointing up (stop gesture)
- Fist closed
- Fingers not aligned horizontally
- Hand moving/shaking

## Safety Features

1. **Timeout Protection**: Won't wait forever (1 minute max)
2. **Stability Check**: Requires 5 seconds of steady hand (prevents accidental triggers)
3. **Reverse Motion**: Safely returns biscuit if no recipient
4. **Visual Feedback**: Shows countdown and hand detection status on screen

## Keys
- **ESC**: Emergency abort at any time
- **Enter**: Start sequence after servo power-on

## Dependencies
- adafruit_servokit
- picamera2
- opencv-python (cv2)
- mediapipe

## Files Used
- `motions/give_biscuit.json`: Recorded motion data
- `smart_biscuit_handover.py`: Main script
