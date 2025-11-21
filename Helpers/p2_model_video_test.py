from ultralytics import YOLO
import cv2, time

url = "http://192.168.xxx.xxx:8080/video"
model = YOLO(r"best.pt") # Put your model path here

cap = cv2.VideoCapture(url)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

prev_time = 0

while True:
    # Flush old frames
    for _ in range(2): cap.grab()

    ret, frame = cap.read()
    if not ret:
        print("⚠️ No frame received")
        continue

    # Resize to speed up YOLO
    frame = cv2.resize(frame, (640, 480))

    # Run detection
    results = model(frame, verbose=False)

    # Draw boxes
    annotated = results[0].plot()

    # Show FPS
    fps = 1 / (time.time() - prev_time) if prev_time else 0
    prev_time = time.time()
    cv2.putText(annotated, f"{fps:.1f} FPS", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("YOLOv8 Stream", annotated)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
