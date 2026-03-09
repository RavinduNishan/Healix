from ultralytics import YOLO
from picamera2 import Picamera2
import cv2

# Load trained model
model = YOLO("models/best.pt")

# Start camera
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640,480)})
picam2.configure(config)
picam2.start()

print("Press Q to quit")

while True:

    frame = picam2.capture_array()

    # Convert 4-channel image to 3-channel BGR
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    # Run detection
    results = model(frame, imgsz=320, conf=0.6)

    annotated = results[0].plot()

    cv2.imshow("Biscuit Detection", annotated)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()