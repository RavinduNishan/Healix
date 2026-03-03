import cv2

gst_pipeline = (
    "libcamerasrc ! "
    "video/x-raw,width=640,height=480,format=RGB ! "
    "videoconvert ! "
    "appsink"
)

cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("Camera failed to open")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Frame failed")
        break

    cv2.imshow("GStreamer Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()