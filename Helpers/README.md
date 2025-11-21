---

# ✅ **README.md (for helpers/ folder)**

Copy-paste this directly into your **helpers/README.md**

---

# Helper Scripts for Tomato Segregator Project

This folder contains **test and debugging scripts** that help verify different parts of the Tomato Segregator system such as:

* Camera feed
* YOLOv8 model
* Arduino communication
* Wired/Wireless video input
* Stabilization testing

These files are **NOT the main project**, but they help you troubleshoot and test features individually.

Below is a simple explanation of each script and what you must change before running it.

---

## 📌 **1) p1_fps_test.py — Test Average FPS of IP Webcam**

**Purpose:**
Checks the average FPS of your **phone camera** using the IP Webcam app.

**You must change:**

```
url = "http://192.168.xxx.xxx:8080/video"
```

Put your phone’s IP address.

**Usage:**
Helps check network lag and performance.

---

## 📌 **2) p2_model_video_test.py — YOLOv8 + IP Webcam Test**

**Purpose:**
Tests YOLOv8 detection directly on your phone camera feed.

**You must change:**

```
url = "http://192.168.xxx.xxx:8080/video"
model = YOLO("best.pt")
```

Use your correct video URL + model path.

**Usage:**
Helps confirm your YOLO model works properly on a live stream.

---

## 📌 **3) p3_arduino&python.py — Full Wireless Sorting Test**

**Purpose:**
Runs YOLOv8 + IP Webcam + Arduino servo control wirelessly.

**You must change:**

```
VIDEO_URL = "http://192.168.xxx.xxx:8080/video"
ARDUINO_IP = "192.168.xxx.xxx"
MODEL_PATH = "best.pt"
```

**Features:**

* Reads Arduino’s active mode (`/task`)
* Detects tomato classes
* Sends commands to Arduino (`/cmd?dir=left` etc.)
* Handles Fresh/Rotten, Red/Green, Small/Large
* Smooths detection (anti-spam)

**Usage:**
This is the full wireless detection script.

---

## 📌 **4) p4_wires_cam_test.py — Wired Camera Test (USB / DroidCam)**

**Purpose:**
Checks if your **wired camera** (USB webcam or DroidCam USB) is working.

**You must change:**

```
cap = cv2.VideoCapture(1)
```

Try camera index `0`, `1`, `2`, or `3` depending on your system.

**Usage:**
Helps switch from slow Wi-Fi feed to fast wired feed.

---

## 📌 **5) p5_fail.py — YOLO + Wired Camera (Basic Version)**

**Purpose:**
First attempt at a **wired camera version** of the sorter.
This script is simpler but keeps the same sorting logic:

**You must change:**

```
CAMERA_INDEX = 1
ARDUINO_IP = "192.168.xxx.xxx"
MODEL_PATH = "best.pt"
```

**Usage:**
Good for testing wired camera + YOLO + Arduino integration.

> Note: replaced later by p6, which is smoother.

---

## 📌 **6) p6_fail.py — Advanced Wired Camera Version (Multithreaded)**

**Purpose:**
A more advanced version that runs:

* Multithreaded video capture
* Stabilization logic
* Arduino communication
* FPS overlay
* Size-based sorting
* Detection smoothing with buffers

This script aims to reduce lag using a background camera thread.

**You must change:**

```
CAMERA_INDEX = 1
ARDUINO_IP = "http://192.168.xxx.xxx"
MODEL_PATH = "best.pt"
```

**Usage:**
Useful for debugging heavy lag issues or testing multi-threaded performance.

---

# 📝 Notes for Users

### 1️⃣ **Your YOLO model path must be correct**

Example:

```
MODEL_PATH = r"C:\Users\YourName\Models\best.pt"
```

### 2️⃣ **If you're using IP Webcam (wireless)**

Make sure phone + laptop + Arduino are on SAME Wi-Fi network.

### 3️⃣ **If you're using Wired Camera**

Try these indices:

```
0 → laptop webcam
1 → DroidCam USB
2 → external USB webcam
```

### 4️⃣ **Arduino must always show an IP like:**

```
192.168.137.xxx
```

Use this IP in your Python file.

### 5️⃣ **Press Q to exit any test script**

---

# ✔ Summary Table

| Script              | Purpose                      | Wireless? | Wired? |
| ------------------- | ---------------------------- | --------- | ------ |
| p1_fps_test         | Test FPS of IP Webcam        | ✔         | ❌      |
| p2_model_video_test | YOLO + IP Webcam detection   | ✔         | ❌      |
| p3_arduino&python   | Full wireless sorting        | ✔         | ❌      |
| p4_wires_cam_test   | Test wired camera only       | ❌         | ✔      |
| p5_fail             | YOLO + wired camera basic    | ❌         | ✔      |
| p6_fail             | YOLO + wired camera advanced | ❌         | ✔      |

---
