#include <WiFiS3.h>
#include <Servo.h>
#include <Wire.h>
#include <Adafruit_SSD1306.h>
#include "Arduino_LED_Matrix.h"

// ---------------- WIFI CONFIG ----------------
char ssid[] = "AAAAAA";          //Put your wifi SSID here
char pass[] = "12345678";       //Put your wifi password here
WiFiServer server(80);

// ---------------- SERVO CONFIG ----------------
Servo myServo;
const int SERVO_HOME = 90;
const int SERVO_LEFT = 5;
const int SERVO_RIGHT = 175;
const int SERVO_DELAY = 1000; // 1 second hold

// ---------------- BUTTON CONFIG ----------------
const int greenBtn = 2;
const int redBtn = 3;
const int blueLBtn = 4;
const int blueRBtn = 5;

// ---------------- OLED CONFIG ----------------
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// ---------------- MATRIX CONFIG ----------------
ArduinoLEDMatrix matrix;

// ---------------- STATE VARIABLES ----------------
int task = 0;
bool isMoving = false;

// ---------------- SETUP ----------------
void setup() {
  Serial.begin(9600);
  while (!Serial);
  delay(2000);
  Serial.println("🔹 Booting Tomato Segregator...");

  myServo.attach(9);
  myServo.write(SERVO_HOME);

  pinMode(greenBtn, INPUT_PULLUP);
  pinMode(redBtn, INPUT_PULLUP);
  pinMode(blueLBtn, INPUT_PULLUP);
  pinMode(blueRBtn, INPUT_PULLUP);

  matrix.begin();
  matrix.clear();

  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("🔹 Booting Tomato Segregator...");
  display.display();
  delay(1500);

  IPAddress ip(192, 168, 137, 200);
  IPAddress gateway(192, 168, 137, 1);
  IPAddress subnet(255, 255, 255, 0);
  WiFi.config(ip, gateway, subnet);
  WiFi.begin(ssid, pass);
  WiFi.setHostname("TomatoSegregator");

  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("Connecting WiFi...");
  display.display();

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  server.begin();
  Serial.println("\n✅ WiFi Connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  display.clearDisplay();
  display.println("✅ WiFi Connected!");
  display.print("IP: ");
  display.println(WiFi.localIP());
  display.display();
  delay(2000);

  showTask(task);
}

// ---------------- LOOP ----------------
void loop() {
  handleManualOverride();

  if (!digitalRead(greenBtn)) {
    task++;
    if (task > 5) task = 0;
    showTask(task);
    delay(300);
  }
  if (!digitalRead(redBtn)) {
    task = 0;
    showTask(task);
    delay(300);
  }

  WiFiClient client = server.available();
  if (client) {
    String request = "";
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        request += c;
        if (c == '\n') break;
      }
    }

    Serial.println(request);

    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: text/plain");
    client.println("Connection: close");
    client.println();

    if (request.indexOf("/task") != -1) {
      client.println(task);
      Serial.println("📤 Sent Task Number: " + String(task));
    }
    else if (request.indexOf("/cmd?dir=left") != -1) {
      Serial.println("➡️ LEFT command received");
      moveServo(SERVO_LEFT, "LEFT");
      client.println("LEFT_OK");
    }
    else if (request.indexOf("/cmd?dir=right") != -1) {
      Serial.println("➡️ RIGHT command received");
      moveServo(SERVO_RIGHT, "RIGHT");
      client.println("RIGHT_OK");
    }
    else if (request.indexOf("/cmd?dir=home") != -1) {
      Serial.println("➡️ HOME command received");
      moveServo(SERVO_HOME, "HOME");
      client.println("HOME_OK");
    }
    else {
      client.println("UNKNOWN");
    }

    client.stop();
  }
}

// ---------------- SERVO MOVEMENT (simplified) ----------------
void moveServo(int angle, const char* direction) {
  if (isMoving) return;
  isMoving = true;

  display.clearDisplay();
  display.setTextSize(2);
  display.setCursor(10, 10);
  display.println("SORTING...");
  display.display();

  // Keep servo attached; just move and return
  myServo.write(angle);
  delay(SERVO_DELAY);

  myServo.write(SERVO_HOME);
  delay(SERVO_DELAY);

  // Small cooldown
  delay(200);

  display.clearDisplay();
  display.setTextSize(2);
  display.setCursor(25, 25);
  display.println(direction);
  display.display();
  delay(400);

  showTask(task);
  isMoving = false;
}


// ---------------- MANUAL BUTTONS ----------------
void handleManualOverride() {
  if (isMoving) return;
  bool blueL = !digitalRead(blueLBtn);
  bool blueR = !digitalRead(blueRBtn);
  if (blueL) moveServo(SERVO_LEFT, "LEFT");
  else if (blueR) moveServo(SERVO_RIGHT, "RIGHT");
}

// ---------------- DISPLAY ----------------
void showTask(int t) {
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(2);

  switch (t) {
    case 0: display.setCursor(30, 25); display.println("IDLE"); break;
    case 1: display.setCursor(0, 25); display.println("Tom/Veg"); break;
    case 2: display.setCursor(0, 25); display.println("Fresh/Rot"); break;
    case 3: display.setCursor(0, 25); display.println("Red/Green"); break;
    case 4: display.setCursor(0, 25); display.println("Small/Large"); break;
    case 5: display.setCursor(25, 25); display.println("MANUAL"); break;
  }

  display.display();
  Serial.print("📟 Current Task: ");
  Serial.println(t);
}
