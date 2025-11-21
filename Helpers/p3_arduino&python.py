from ultralytics import YOLO
import cv2, requests, time, collections

# ---------------- CONFIG ----------------
VIDEO_URL = "http://192.168.xxx.xxx:8080/video"  # <-- change xx to your phone's IP
ARDUINO_IP = "192.168.xxx.xxx" #<-- change xx to your Arduino's IP
MODEL_PATH = r"best.pt" #<-- your model path

CONF_THRESHOLD = 0.5
FRAME_SKIP = 2
COOLDOWN = 2.5
PERSIST_FRAMES = 4
SIZE_THRESHOLD = 39000   # <-- your given area threshold

# ---------------- CLASS SETS ----------------
TOMATO_CLASSES = ["red_tomato", "green_tomato", "rotten_tomato"]
VEG_CLASSES    = ["onion", "potato"]
FRESH_CLASSES  = ["red_tomato", "green_tomato"]
ROTTEN_CLASSES = ["rotten_tomato"]
GREEN_CLASSES  = ["green_tomato"]
RED_CLASSES    = ["red_tomato"]

# ---------------- FUNCTIONS ----------------
def get_current_task(arduino_ip):
    """Reads current mode from Arduino"""
    try:
        res = requests.get(f"http://{arduino_ip}/task", timeout=2)
        if res.status_code == 200:
            return int(res.text.strip())
    except Exception:
        pass
    print("⚠️ Arduino unreachable, defaulting to 1")
    return 1

# ---------------- SETUP ----------------
model = YOLO(MODEL_PATH)
cap = cv2.VideoCapture(VIDEO_URL)
if not cap.isOpened():
    print("❌ Cannot open video stream")
    exit()

CURRENT_TASK = get_current_task(ARDUINO_IP)
print(f"🔁 Arduino reports Task {CURRENT_TASK}")

prev_dir = None
last_task_check = 0
history = collections.deque(maxlen=PERSIST_FRAMES)
frame_idx = 0

print(f"✅ Running detection for Task {CURRENT_TASK}. Press Q to quit.")

# ---------------- MAIN LOOP ----------------
while True:
    for _ in range(3): cap.grab()
    ret, frame = cap.read()
    if not ret: continue

    frame_idx += 1
    if frame_idx % FRAME_SKIP != 0: continue

    results = model(frame, verbose=False)
    annotated = results[0].plot()
    direction = None
    detected_label = None

    if results[0].boxes:
        best = max(results[0].boxes, key=lambda b: float(b.conf[0]))
        cls = model.names[int(best.cls[0])]
        conf = float(best.conf[0])
        if conf > CONF_THRESHOLD:
            detected_label = cls
            # ---- Task-based rules ----
            if CURRENT_TASK == 1:               # Tomato / Vegetable
                direction = "left"  if cls in TOMATO_CLASSES else "right" if cls in VEG_CLASSES else None
            elif CURRENT_TASK == 2:             # Fresh / Rotten
                direction = "left"  if cls in FRESH_CLASSES else "right" if cls in ROTTEN_CLASSES else None
            elif CURRENT_TASK == 3:             # Red / Green
                direction = "left"  if cls in GREEN_CLASSES else "right" if cls in RED_CLASSES else None
            elif CURRENT_TASK == 4:             # Small / Large (by area)
                x1, y1, x2, y2 = map(int, best.xyxy[0])
                area = (x2 - x1) * (y2 - y1)
                direction = "left" if area < SIZE_THRESHOLD else "right"
                detected_label = f"{'Small' if area < SIZE_THRESHOLD else 'Large'} Tomato ({area})"

    # ---- Stabilize detection ----
    history.append(direction)
    stable_dir = max(set(history), key=history.count) if history else None

    # ---- Send to Arduino ----
    if stable_dir and stable_dir != prev_dir:
        try:
            requests.get(f"http://{ARDUINO_IP}/cmd?dir={stable_dir}", timeout=1.0)
            print(f"➡️ Sent: {stable_dir} ({detected_label})")
            prev_dir = stable_dir
        except requests.RequestException:
            print("⚠️ Arduino unreachable")

    # ---- Display ----
    cv2.putText(annotated, f"Task {CURRENT_TASK} | {detected_label}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
    cv2.imshow("Tomato Segregator", annotated)

    # ---- Periodic mode refresh ----
    if time.time() - last_task_check > 5:
        new_task = get_current_task(ARDUINO_IP)
        if new_task != CURRENT_TASK:
            CURRENT_TASK = new_task
            print(f"🔁 Mode changed to Task {CURRENT_TASK}")
        last_task_check = time.time()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
