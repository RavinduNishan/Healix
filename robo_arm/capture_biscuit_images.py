from picamera2 import Picamera2
import cv2
import os

# Folder path
save_folder = "Healix/robo_arm/images"

# Create folder if it doesn't exist
os.makedirs(save_folder, exist_ok=True)

# Start camera
picam2 = Picamera2()

config = picam2.create_preview_configuration(
    main={"size": (640, 480)}
)

picam2.configure(config)
picam2.start()

count = 0

print("Press S to save image")
print("Press Q to quit")

while True:
    
    frame = picam2.capture_array()

    cv2.imshow("Camera", frame)

    key = cv2.waitKey(1) & 0xFF

    # Save image
    if key == ord('s'):
        filename = os.path.join(save_folder, f"img_{count}.jpg")
        cv2.imwrite(filename, frame)
        print("Saved:", filename)
        count += 1

    # Quit program
    if key == ord('q'):
        break

cv2.destroyAllWindows()