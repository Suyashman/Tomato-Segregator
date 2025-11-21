---

# Smart Tomato Segregator (YOLOv8 + Arduino WiFi Automation)

This project uses YOLOv8, an Arduino UNO R4 WiFi board, a servo motor, an OLED display, and a phone/webcam to automatically classify and physically sort tomatoes and vegetables in real-time.

The system detects objects using YOLOv8, selects a sorting direction based on the active mode, and wirelessly sends commands to the Arduino to operate a servo mechanism.

---

## Files in This Folder

| File               | Description                                                                                                   |
| ------------------ | ------------------------------------------------------------------------------------------------------------- |
| **best.pt**        | YOLOv8 model trained on a small custom dataset (see dataset notes below).                                     |
| **p7_running.py**  | Main Python script for real-time detection and wireless sorting. Supports wired camera or IP Webcam.          |
| **p3_running.ino** | Arduino UNO R4 WiFi firmware. Handles WiFi server, OLED display, LED matrix, button modes, and servo control. |

---

# Features

### 1. Tomato vs Other Vegetables

Tomato → Left
Onion or Potato → Right

### 2. Fresh vs Rotten

Fresh Tomato → Left
Rotten Tomato (dummy rotten) → Right

### 3. Red vs Green Tomato

Green Tomato → Left
Red Tomato → Right

### 4. Small vs Large Tomato

Uses bounding box area.
Threshold ≈ **45,000 px²** (adjustable inside Python code).

### 5. Manual Mode

Servo is controlled using two physical buttons.

---

# Camera Options

### Wired (Recommended)

Works with:

* DroidCam USB mode
* USB webcams

Set in Python:

```
CAMERA_INDEX = 1
```

Try 0/1/2 if needed.

### Wireless (Optional)

Uses the **IP Webcam** Android app.

Set:

```
CAMERA_URL = "http://your_phone_ip:8080/video"
```

---

# Important Note About the Model (best.pt)

This YOLOv8 model **does not detect real rotten tomatoes**.

The "rotten tomato" class was created using **dummy samples**:

* Normal tomatoes
* With black marker dots drawn to simulate rot

Because of this, the model detects **dark spots**, not actual biological spoilage.

### If you want accurate real rot detection:

You must **train your own YOLOv8 model** using real-world data.

---

# Dataset Information

This model was trained on a **very small** custom dataset created using **Roboflow**.

### Dataset Split

| Split      | Percent | Images |
| ---------- | ------- | ------ |
| Train      | 90%     | 453    |
| Validation | 8%      | 40     |
| Test       | 2%      | 10     |

### Classes

* red_tomato
* green_tomato
* rotten_tomato (dummy)
* onion
* potato

### Preprocessing

* Auto-Orient: Enabled

### Augmentations

* Horizontal Flip
* Random Crop (0–20% zoom)
* Rotation (−15° to +15°)
* Horizontal Shear (±5°)
* Brightness (±20%)
* Exposure (±10%)
* Blur (0–2px)
* Random Noise (up to 0.22%)

### Dataset Link

[https://app.roboflow.com/suyashman/tomato-segregation-cpbdd/3](https://app.roboflow.com/suyashman/tomato-segregation-cpbdd/3)

---

# Running the Main Python Script (p7_running.py)

## 1. Install Dependencies

```
pip install ultralytics opencv-python requests
```

## 2. Configure Settings

### Set camera source

Wired camera:

```
CAMERA_INDEX = 1
```

Wireless camera:

```
CAMERA_URL = "http://192.168.xxx.xxx:8080/video"
```

### Set Arduino IP

```
ARDUINO_IP = "http://192.168.137.xxx"
```

### Set model path

```
MODEL_PATH = "best.pt"
```

## 3. Run the Script

```
python p7_running.py
```

Press **Q** to exit.

---

# Arduino Setup (p3_running.ino)

### Hardware Connections

| Pin        | Component                 |
| ---------- | ------------------------- |
| 9          | Servo (sorting arm)       |
| 2          | Green button – cycle mode |
| 3          | Red button – idle mode    |
| 4          | Blue left button          |
| 5          | Blue right button         |
| I2C        | OLED 128×64 display       |
| LED Matrix | Built-in UNO R4           |

### Arduino WiFi Routes

| Route            | Description                 |
| ---------------- | --------------------------- |
| `/task`          | Returns current mode number |
| `/cmd?dir=left`  | Move servo left             |
| `/cmd?dir=right` | Move servo right            |
| `/cmd?dir=home`  | Move servo to center        |

---

# Mode Overview

| Task | Mode            | Left Output       | Right Output      |
| ---- | --------------- | ----------------- | ----------------- |
| 0    | Idle            | —                 | —                 |
| 1    | Tomato vs Other | Tomato            | Onion/Potato      |
| 2    | Fresh vs Rotten | Fresh             | Rotten            |
| 3    | Red vs Green    | Green             | Red               |
| 4    | Small vs Large  | Small             | Large             |
| 5    | Manual          | Button-controlled | Button-controlled |

---

# How the System Works (Pipeline)

1. Camera captures video.
2. Python (p7_running.py) runs YOLOv8 detection.
3. Detection → class → sorting rule (based on active Arduino task).
4. Python sends sorting direction using WiFi (`/cmd?dir=`).
5. Arduino moves servo to left or right, returns home.
6. OLED and LED matrix update current mode/status.
7. Green/red/blue physical buttons control modes and manual actions.

---

# Recommendations

* Train your own YOLOv8 model with **real rotten tomatoes** for better accuracy.
* Use **wired camera** to reduce latency.
* Adjust `SIZE_THRESHOLD` to match your camera distance and object size.
* Use good lighting for best YOLO results.

---
