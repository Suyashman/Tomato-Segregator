import cv2
import time
import requests
from collections import deque, Counter
from ultralytics import YOLO
from threading import Thread

# ===================== USER CONFIG =====================
# ===================== USER CONFIG =====================
# CAMERA_URL  = "http://192.168.xxx.xxx:8080/video"   # (OLD)
CAMERA_INDEX = 1     # usually 1 or 2 for DroidCam wired
ARDUINO_IP  = "http://192.168.xxx.xxx"
MODEL_PATH  = r"best.pt"


CONF_THRESHOLD   = 0.5           # YOLO confidence
FRAME_SKIP       = 2             # run YOLO every Nth frame
RESIZE_SHAPE     = (640, 480)    # displayed frame size
SMOOTH_WINDOW    = 10            # frames for temporal smoothing
COOLDOWN_SEC     = 1.5           # gap between servo commands
STABILIZE_SEC    = 1.0           # wait time to confirm stable detection
HTTP_TIMEOUT_SEC = 5.0           # wait long enough for Arduino reply
SIZE_THRESHOLD   = 45000         # bbox area threshold for Task 4

# ===================== VIDEO THREAD =====================
class VideoStream:
    def __init__(self, src):
        # Open the camera with MSMF backend for DroidCam
        self.cap = cv2.VideoCapture(src, cv2.CAP_MSMF)
        time.sleep(2)  # allow camera to warm up

        if not self.cap.isOpened():
            raise RuntimeError(f"❌ Cannot open camera source {src}")

        # Initialize frame and control flags
        self.frame = None
        self.stopped = False

        # Start the background thread
        Thread(target=self.update, daemon=True).start()

    def update(self):
        """Continuously grab frames from the camera"""
        while not self.stopped:
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame

    def read(self):
        """Return the most recent frame"""
        return self.frame

    def stop(self):
        """Stop the camera thread"""
        self.stopped = True
        self.cap.release()


# ===================== ARDUINO HELPERS =====================
def get_task():
    try:
        r = requests.get(f"{ARDUINO_IP}/task", timeout=HTTP_TIMEOUT_SEC)
        return int(r.text.strip())
    except Exception:
        return -1

def send_command(cmd):
    try:
        # Updated to match Arduino route
        r = requests.get(f"{ARDUINO_IP}/cmd?dir={cmd}", timeout=HTTP_TIMEOUT_SEC)
        print(f"➡️ Sent to Arduino: /cmd?dir={cmd} → {r.text.strip()}")
        return True
    except Exception as e:
        print(f"⚠️ Connection error: {e}")
        return False


# ===================== DISPLAY HELPERS =====================
TASK_NAMES = {
    0: "Task 0: Idle",
    1: "Task 1: Tomato vs Other",
    2: "Task 2: Fresh vs Rotten",
    3: "Task 3: Red vs Green",
    4: "Task 4: Size Based",
    5: "Task 5: Manual Buttons",
}

def draw_overlay(img, fps, task, stable_label):
    htxt = TASK_NAMES.get(task, f"Task {task}")
    cv2.putText(img, f"{htxt}", (10, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.putText(img, f"Stable: {stable_label}", (10, 58),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(img, f"FPS: {fps:.1f}", (10, 88),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

# ===================== MAIN =====================
def main():
    print("🔹 Loading YOLOv8 model...")
    model = YOLO(MODEL_PATH)
    print("✅ Model loaded.")

    vs = VideoStream(CAMERA_INDEX)
    time.sleep(2)
    print("✅ Camera stream started. Press 'q' to quit.\n")

    detection_buffer = deque(maxlen=SMOOTH_WINDOW)
    frame_count = 0
    last_task_poll = 0.0
    current_task = 0
    last_cmd_time = 0.0
    last_sent_cmd = None
    fps = 0.0
    fps_tick = time.time()
    last_boxes_xywh = None
    empty_frame_count = 0
    current_seen_label = None
    first_seen_time = None

    while True:
        frame = vs.read()
        if frame is None:
            continue

        frame = cv2.resize(frame, RESIZE_SHAPE)
        frame_count += 1

        # periodically refresh task from Arduino (every ~2.5s)
        now = time.time()
        if now - last_task_poll > 2.5:
            t = get_task()
            if t != -1 and t != current_task:
                current_task = t
                print(f"📟 Current Task (from Arduino): {current_task}")
            last_task_poll = now

        # ------------------- YOLO Detection -------------------
        detections_this_frame = []
        if frame_count % FRAME_SKIP == 0:
            results = model(frame, conf=CONF_THRESHOLD, imgsz=640, verbose=False)
            boxes = results[0].boxes
            names = results[0].names

            try:
                last_boxes_xywh = boxes.xywh.cpu().numpy() if boxes is not None else None
            except Exception:
                last_boxes_xywh = None

            if boxes is not None and boxes.cls is not None and len(boxes.cls) > 0:
                detections_this_frame = [names[int(c)] for c in boxes.cls.cpu().numpy().astype(int)]
                main_label = Counter(detections_this_frame).most_common(1)[0][0]
                detection_buffer.append(main_label)
            annotated = results[0].plot()
        else:
            annotated = frame

        # ------------------- Detection Timeout -------------------
        if len(detections_this_frame) == 0:
            empty_frame_count += 1
        else:
            empty_frame_count = 0

        if empty_frame_count > 8:
            detection_buffer.clear()
            current_seen_label = None
            first_seen_time = None

        if len(detection_buffer) > 0:
            stable_label = Counter(detection_buffer).most_common(1)[0][0]
        else:
            stable_label = "none"

        # ------------------- Stabilization Logic -------------------
        if stable_label != "none":
            if stable_label != current_seen_label:
                current_seen_label = stable_label
                first_seen_time = time.time()  # new label detected
            else:
                # if same label persists for 1 second
                if time.time() - first_seen_time >= STABILIZE_SEC:
                    confirmed_label = current_seen_label
                else:
                    confirmed_label = "none"  # still stabilizing
        else:
            confirmed_label = "none"
            current_seen_label = None
            first_seen_time = None

        # ------------------- FPS Update -------------------
        if frame_count % 10 == 0:
            now2 = time.time()
            fps = 10.0 / max(1e-6, (now2 - fps_tick))
            fps_tick = now2

        draw_overlay(annotated, fps, current_task, confirmed_label)

        # ------------------- DECISION LOGIC -------------------
        if current_task in (1, 2, 3, 4) and confirmed_label != "none":
            if (time.time() - last_cmd_time) > COOLDOWN_SEC:
                cmd_to_send = None
                message = ""

                # Task 1: Tomato vs Other
                if current_task == 1:
                    if ("tomato" in confirmed_label) or \
                    (confirmed_label in ("red_tomato", "green_tomato", "rotten_tomato")):
                        cmd_to_send = "left"
                        message = f"🍅 Tomato detected → LEFT ({confirmed_label})"
                    else:
                        cmd_to_send = "right"
                        message = f"🥔 Other Veg detected → RIGHT ({confirmed_label})"

                # Task 2: Fresh vs Rotten
                elif current_task == 2:
                    if confirmed_label == "rotten_tomato":
                        cmd_to_send = "right"
                        message = f"🧫 Rotten Tomato → RIGHT"
                    elif confirmed_label in ("red_tomato", "green_tomato"):
                        cmd_to_send = "left"
                        message = f"🍅 Fresh Tomato → LEFT"

                # Task 3: Red vs Green
                elif current_task == 3:
                    if confirmed_label == "red_tomato":
                        cmd_to_send = "left"
                        message = f"🔴 Red Tomato → LEFT"
                    elif confirmed_label == "green_tomato":
                        cmd_to_send = "right"
                        message = f"🟢 Green Tomato → RIGHT"

                # Task 4: Size-based (based on bounding box area)
                elif current_task == 4 and last_boxes_xywh is not None and len(last_boxes_xywh) > 0:
                    w, h = last_boxes_xywh[0][2], last_boxes_xywh[0][3]
                    area = float(w) * float(h)
                    cmd_to_send = "left" if area > SIZE_THRESHOLD else "right"
                    size_type = "LARGE" if area > SIZE_THRESHOLD else "SMALL"
                    message = f"📏 Size: {area:.3f} → {size_type} → {cmd_to_send.upper()}"

                # Send to Arduino & print readable result
                if cmd_to_send:
                    if cmd_to_send != last_sent_cmd or (time.time() - last_cmd_time) > (COOLDOWN_SEC * 2):
                        print(message)
                        if send_command(cmd_to_send):
                            last_cmd_time = time.time()
                            last_sent_cmd = cmd_to_send


        # ------------------- DISPLAY -------------------
        cv2.imshow("🍅 Tomato Segregator (YOLOv8 + Arduino WiFi)", annotated)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    vs.stop()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
