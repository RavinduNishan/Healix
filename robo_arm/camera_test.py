from picamera2 import Picamera2
import cv2

# Initialize camera
picam2 = Picamera2()

# Camera configuration
picam2.configure(picam2.create_preview_configuration(
    main={"size": (640, 480)}
))

picam2.start()

print("Camera started. Press Q to exit.")

while True:
    frame = picam2.capture_array()

    cv2.imshow("Raspberry Pi Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()