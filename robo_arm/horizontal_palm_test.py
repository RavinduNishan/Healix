from picamera2 import Picamera2
import cv2
import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

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

print("Horizontal Plate Palm Detection Started")


# --------------------------
# Helpers
# --------------------------

def is_finger_extended(lm, tip, pip):
    return lm.landmark[tip].y < lm.landmark[pip].y

def fingers_open(lm):
    fingers = [(8,6),(12,10),(16,14),(20,18)]
    return all(is_finger_extended(lm,t,p) for t,p in fingers)


def is_horizontal_plate_palm(lm):

    wrist = np.array([lm.landmark[0].x,
                      lm.landmark[0].y,
                      lm.landmark[0].z])

    index_mcp = np.array([lm.landmark[5].x,
                          lm.landmark[5].y,
                          lm.landmark[5].z])

    pinky_mcp = np.array([lm.landmark[17].x,
                          lm.landmark[17].y,
                          lm.landmark[17].z])

    # Palm plane vectors
    v1 = index_mcp - wrist
    v2 = pinky_mcp - wrist

    normal = np.cross(v1, v2)
    normal = normal / np.linalg.norm(normal)

    nx, ny, nz = normal

    # Plate hand condition:
    # Palm surface facing UP (normal mostly vertical)
    vertical_normal = abs(ny) > 0.7

    # Should NOT face camera strongly
    not_camera_facing = abs(nz) < 0.4

    # Should NOT be sideways
    not_sideways = abs(nx) < 0.6

    return vertical_normal and not_camera_facing and not_sideways


# --------------------------
# Main Loop
# --------------------------

while True:
    frame = picam2.capture_array()
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for lm in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)

            if fingers_open(lm) and is_horizontal_plate_palm(lm):
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

    cv2.imshow("Plate Palm Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cv2.destroyAllWindows()
picam2.stop()