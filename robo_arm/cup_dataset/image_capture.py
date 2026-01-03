import cv2
import os

# Create folder
os.makedirs("images", exist_ok=True)

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

if not cap.isOpened():
    print("ERROR: Could not open camera")
    exit()
    
count = 0

print("Press S to save image | Q to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera not detected")
        break

    # ROTATE 180 DEGREE (IMPORTANT)
    frame = cv2.rotate(frame, cv2.ROTATE_180)

    cv2.imshow("Camera View", frame)

    key = cv2.waitKey(1)

    if key == ord('s'):
        filename = f"images/cup_{count}.jpg"
        cv2.imwrite(filename, frame)
        print("Saved:", filename)
        count += 1

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
