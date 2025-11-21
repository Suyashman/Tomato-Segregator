🍅 Smart Tomato Segregator (YOLOv8 + Arduino WiFi Automation)
Real-time object detection and automatic sorting system using YOLOv8, Arduino UNO R4 WiFi, servo motor, OLED display, and phone/laptop camera.
This project performs 5 different sorting modes using YOLOv8 and sends commands wirelessly to the Arduino to control a servo-based segregation mechanism.

READ LINE 41 ----------< DISCLAIMER >----------

📂 Files in This Folder : 
best.pt	        - YOLOv8 object detection model (trained by me on a small custom dataset — see dataset notes below).
p7_running.py   - Main Python script for running YOLOv8 + real-time sorting using a wired phone camera (DroidCam USB) or webcam.
p3_running.ino  -	Arduino UNO R4 WiFi code. Receives commands over WiFi, updates OLED, switches modes, and moves the servo.

⚙️ System Features
✔ 1. Tomato vs Other Vegetables
(tomato → left, onion/potato → right)

✔ 2. Fresh vs Rotten
(fresh → left, rotten → right)

✔ 3. Red vs Green Tomato
(green → left, red → right)

✔ 4. Small vs Large Tomato
Based on bounding-box area
(Threshold ≈ 45,000 px², tunable)

✔ 5. Manual Mode
Left/right servo movement using buttons


📸 Camera Options
Wired Mode (Recommended for less lag - delay)
Use DroidCam USB or a webcam for lag-free video.
Set:  CAMERA_INDEX = 1

Wireless Mode (Optional)
Use the IP Webcam Android app.
Set:  CAMERA_URL = "http://your_phone_ip:8080/video"

The main script supports either mode.

🧠 About the Model (Important Disclaimer)
⚠️ The “rotten tomatoes” in this dataset are dummy rotten
They are NOT real spoiled tomatoes.
They are normal tomatoes with black marker spots to simulate rot.
Because of this, the model detects black spots, not true rotting patterns.

This was done just for demonstration purposes , easy implementation 
For actual implementation , you need to train your own model with real rotten tomatoes


📦 Dataset Information
The model was trained using Roboflow on a very small dataset:
Augmentation was applied : ()
Dataset Split
Split	Percent	Images
Train	  90%	      453
Valid	  8%	      40
Test	  2%	      10
 
Classes
red_tomato
green_tomato
rotten_tomato (dummy)
onion
potato

Dataset Link
📎 https://app.roboflow.com/suyashman/tomato-segregation-cpbdd/3

-----------------------------------------------------------------------------------------
🔔 Important Note for Users
If you want accurate real-world results:

👉 Train your own YOLOv8 model.
You can: Collect your own tomatoes
Or place marker dots depending on rot level
Or fully create your own classification style
Upload dataset to Roboflow
Export YOLOv8 format
Train using: yolo detect train data=data.yaml model=yolov8n.pt epochs=50 imgsz=640
My included model (best.pt) is only a demo, not production-ready.
-----------------------------------------------------------------------------------------



🧪 How to Run p7_running.py (Main Script)
1️⃣ Install dependencies
pip install ultralytics opencv-python requests

2️⃣ Set your camera
Inside the script:
Wired:
CAMERA_INDEX = 1
Wireless:
CAMERA_URL = "http://192.168.xxx.xxx:8080/video"

3️⃣ Set your Arduino IP
ARDUINO_IP = "http://192.168.137.xxx"

4️⃣ Set your model path
MODEL_PATH = "best.pt"

5️⃣ Run:
python p7_running.py

Press Q to exit.



🤖 Arduino Setup (p3_running.ino)
Hardware connected:
Pin	Component
9	Servo
2	Green button (next mode)
3	Red button (idle mode)
4	Blue left (manual)
5	Blue right (manual)
I2C	OLED 128×64
LED Matrix	Internal    (Optional/ Only works in Arduino R4 Wifi)


🧭 How the System Works Together

Camera → Python script → YOLOv8 detection
YOLOv8 picks best class
Code maps class → direction based on active Arduino mode
Python sends WiFi command to Arduino
Arduino moves servo → returns to home
OLED + LED Matrix display status
Buttons switch modes manually


📦 Modes Overview (Arduino-controlled)
Task	Mode	Left	Right
0	Idle	—	—
1	Tomato vs Veg	Tomato	Onion/Potato
2	Fresh vs Rotten	Fresh	Rotten
3	Red vs Green	Green	Red
4	Small vs Large	Small	Large
5	Manual	Button controlled	Button controlled


🛠️ Future Improvements
Real rotten tomato dataset
Add conveyor belt with timed servo control
Add more vegetable classes
Add edge device inference (Nvidia Jetson / RPi)
Improve stabilization logic for low light


🚀 Final Notes
This system is built to be easy to modify, extend, and retrain.
You can plug in any trained YOLOv8 model and update your Arduino logic accordingly.
If you build your own dataset on Roboflow, you will get much better results than the included model.


-----------------------------------------------------------------------------------------------
My notes : 
This model is really cost effective , it can be built for less than 1,000 INR , practical for farmers and low income households that require segregation for their crop harvests.
This detection machine is small in size , soo small that it can fit inside a two wheeler's storage.
The wireless connection causes some lag of about 2 seconds , which can cause the machine to hang and give wrong segregation 
Wired connection is better. However the wireless mode can be further optimized.
