import cv2

cap = cv2.VideoCapture(1)  # Try 1, 2, or 3 if 0 doesn’t show DroidCam feed

while True:
    ret, frame = cap.read()
    if not ret:
        print("No frame captured")
        break
    cv2.imshow("Phone Camera (USB)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
