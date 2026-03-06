from picamera2 import Picamera2
import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Camera setup
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640,480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

print("Palm + Straight Horizontal Fingers Detection Started")

# ----------- Check if fingers extended horizontally -----------

def fingers_horizontal_extended(lm):
    # Get fingertip positions (index, middle, ring, pinky)
    tips = [8, 12, 16, 20]
    
    # Check 1: All fingertips should be in a horizontal line (similar y-coordinates)
    ys = [lm.landmark[i].y for i in tips]
    y_diff = max(ys) - min(ys)
    
    if y_diff > 0.1:  # Allow some tolerance
        return False
    
    # Check 2: Fingertips should be extended outward (check x spread)
    xs = [lm.landmark[i].x for i in tips]
    x_spread = max(xs) - min(xs)
    
    # Fingers should span a reasonable width when extended
    if x_spread < 0.15:
        return False
    
    return True


# ----------- Main loop -----------

while True:

    frame = picam2.capture_array()

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb)

    if results.multi_hand_landmarks:

        for lm in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)

            if fingers_horizontal_extended(lm):

                cv2.putText(frame,
                            "READY FOR BISCUIT",
                            (40,100),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0,255,0),
                            3)

            else:

                cv2.putText(frame,
                            "Palm Not Valid",
                            (40,100),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0,0,255),
                            2)

    cv2.imshow("Palm Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cv2.destroyAllWindows()
picam2.stop()