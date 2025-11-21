import cv2
import time

# 🔹 Replace with your phone's IP Webcam video URL
# Android IP Webcam app should be running on your phone, connected to the same wifi as laptop/PC
url = "http://192.168.xxx.xxx:8080/video"  # <-- change xx to your phone's IP

cap = cv2.VideoCapture(url)

if not cap.isOpened():
    print("❌ Failed to open video stream.")
    exit()

frame_count = 0
start_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Frame not received!")
        break

    frame_count += 1
    elapsed_time = time.time() - start_time
    avg_fps = frame_count / elapsed_time if elapsed_time > 0 else 0

    # Display average FPS
    cv2.putText(frame, f"Avg FPS: {avg_fps:.2f}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("IP Webcam Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
