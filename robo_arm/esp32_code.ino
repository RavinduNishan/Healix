#include <WiFi.h>
#include <HTTPClient.h>
#include <Firebase_ESP_Client.h>
#include <SPI.h>
#include <Wire.h>
#include <MPU6050.h>
#include "time.h"

// ---------------- WIFI ----------------
#define WIFI_SSID "Galaxy M210"
#define WIFI_PASSWORD "12345679"

// ---------------- FIREBASE ----------------
#define API_KEY "YOUR_API_KEY"
#define DATABASE_URL "YOUR_DATABASE_URL"
#define USER_EMAIL "YOUR_USER_EMAIL"
#define USER_PASSWORD "YOUR_USER_PASSWORD"




// ---------------- ROBOT SERVER ----------------
String serverName = "http://10.142.69.43:5000/run_script";

// ---------------- PINS ----------------
#define PRESSURE_PIN 35
#define CS_PIN 5

// ---------------- MPU6050 ----------------
MPU6050 mpu;
int16_t ax_mpu, ay_mpu, az_mpu;
int16_t gx_mpu, gy_mpu, gz_mpu;

float Ax; // acceleration X
String lastDirection = "";

// Movement threshold
float moveThreshold = 0.8;

// ---------------- FIREBASE ----------------
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

// ---------------- TIME ----------------
const char* ntpServer = "pool.ntp.org";

// ---------------- TIMERS ----------------
unsigned long lastMotionRead = 0;
unsigned long motionInterval = 100;

unsigned long lastSensorRead = 0;
unsigned long sensorInterval = 500;

// ---------------- BUFFER ----------------
#define BUFFER_SIZE 10
int16_t xBuffer[BUFFER_SIZE];
int16_t yBuffer[BUFFER_SIZE];
int16_t zBuffer[BUFFER_SIZE];
int bufferIndex = 0;

// ---------------- PRESSURE ----------------
bool systemArmed = false;
int pressureCount = 0;
bool pressStarted = false;
bool pressurePressed = false;

unsigned long firstPressTime = 0;
unsigned long pressWindow = 7000;

int pressureThreshold = 1000;


// ---------------- ADXL362 ----------------
void writeRegister(byte reg, byte value)
{
  digitalWrite(CS_PIN, LOW);
  SPI.transfer(0x0A);
  SPI.transfer(reg);
  SPI.transfer(value);
  digitalWrite(CS_PIN, HIGH);
}

void readXYZ(int16_t &x, int16_t &y, int16_t &z)
{
  digitalWrite(CS_PIN, LOW);
  SPI.transfer(0x0B);
  SPI.transfer(0x0E);

  x = SPI.transfer(0x00);
  x |= SPI.transfer(0x00) << 8;

  y = SPI.transfer(0x00);
  y |= SPI.transfer(0x00) << 8;

  z = SPI.transfer(0x00);
  z |= SPI.transfer(0x00) << 8;

  digitalWrite(CS_PIN, HIGH);
}


// ---------------- WIFI ----------------
void connectWiFi()
{
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting WiFi");

  while (WiFi.status() != WL_CONNECTED)
  {
    Serial.print(".");
    delay(500);
  }

  Serial.println("\nWiFi Connected");
}


// ---------------- FIREBASE ----------------
void initFirebase()
{
  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;

  auth.user.email = USER_EMAIL;
  auth.user.password = USER_PASSWORD;

  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);

  Serial.println("Waiting Firebase Auth");

  while (auth.token.uid == "")
  {
    Serial.print(".");
    delay(1000);
  }

  Serial.println("\nFirebase Ready");
}


// ---------------- ROBOT ----------------
void triggerRobot(String scriptName)
{
  if (WiFi.status() == WL_CONNECTED)
  {
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    String jsonPayload = "{\"script\":\"" + scriptName + "\"}";
    int httpResponseCode = http.POST(jsonPayload);

    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);

    http.end();
  }
}


// ---------------- SETUP ----------------
void setup()
{
  Serial.begin(115200);

  pinMode(PRESSURE_PIN, INPUT);

  SPI.begin(18,19,23,CS_PIN);
  pinMode(CS_PIN, OUTPUT);
  digitalWrite(CS_PIN, HIGH);

  delay(100);
  writeRegister(0x2D,0x02);

  // MPU6050 INIT
  Wire.begin(21,22);
  mpu.initialize();

  if (!mpu.testConnection()) {
    Serial.println("MPU6050 FAILED");
  } else {
    Serial.println("MPU6050 READY");
  }

  connectWiFi();

  configTime(19800,0,ntpServer);

  time_t now = time(nullptr);
  while (now < 100000)
  {
    delay(500);
    Serial.print(".");
    now = time(nullptr);
  }

  Serial.println("\nTime Ready");

  initFirebase();
}


// ---------------- LOOP ----------------
void loop()
{
  // -------- PRESSURE + MPU --------
  if (millis() - lastSensorRead >= sensorInterval)
  {
    lastSensorRead = millis();

    int pressure = analogRead(PRESSURE_PIN);

    // MPU READ
    mpu.getMotion6(&ax_mpu, &ay_mpu, &az_mpu, &gx_mpu, &gy_mpu, &gz_mpu);

    Ax = ax_mpu / 16384.0;

    Serial.print("Pressure: ");
    Serial.print(pressure);

    Serial.print(" | Ax: ");
    Serial.print(Ax);

    // -------- MOVEMENT DETECTION --------

    // RIGHT
    if (Ax > moveThreshold && lastDirection != "RIGHT") {
      Serial.println(" ---> MOVE RIGHT");
      lastDirection = "RIGHT";
      delay(300);
    }

    // LEFT
    else if (Ax < -moveThreshold && lastDirection != "LEFT") {
      Serial.println(" ---> MOVE LEFT");
      lastDirection = "LEFT";
      if (systemArmed) {
        triggerRobot("biscuit_main");
        systemArmed = false; // Disarm after triggering
      }
      delay(300);
    }

    // STILL
    else if (Ax > -0.3 && Ax < 0.3) {
      lastDirection = "";
      Serial.println(" ---> STILL");
    }
    else {
      Serial.println();
    }


    // -------- PRESS LOGIC --------
    if (pressure > pressureThreshold && !pressurePressed)
    {
      pressurePressed = true;

      if (!pressStarted)
      {
        pressStarted = true;
        firstPressTime = millis();
        pressureCount = 1;
        Serial.println("Press started");
      }
      else
      {
        pressureCount++;
        Serial.print("Count: ");
        Serial.println(pressureCount);
      }

      if (pressureCount >= 3)
      {
        if (millis() - firstPressTime <= pressWindow)
        {
          systemArmed = true;
          Serial.println("SYSTEM ARMED");
        }

        pressureCount = 0;
        pressStarted = false;
      }
    }

    if (pressure < pressureThreshold)
    {
      pressurePressed = false;
    }

    if (pressStarted && (millis() - firstPressTime > pressWindow))
    {
      Serial.println("Timeout");
      pressureCount = 0;
      pressStarted = false;
    }
  }

  // -------- ADXL362 --------
  if (millis() - lastMotionRead >= motionInterval)
  {
    lastMotionRead = millis();

    int16_t x,y,z;
    readXYZ(x,y,z);

    xBuffer[bufferIndex] = x;
    yBuffer[bufferIndex] = y;
    zBuffer[bufferIndex] = z;

    bufferIndex++;

    if(bufferIndex >= BUFFER_SIZE)
    {
      FirebaseJson json;

      for(int i=0;i<BUFFER_SIZE;i++)
      {
        json.set("samples/"+String(i)+"/x",xBuffer[i]);
        json.set("samples/"+String(i)+"/y",yBuffer[i]);
        json.set("samples/"+String(i)+"/z",zBuffer[i]);
      }

      json.set("timestamp", millis());

      if(Firebase.RTDB.pushJSON(&fbdo,"/patient_data_new",&json))
      {
        Serial.println("ADXL sent");
      }
      else
      {
        Serial.println(fbdo.errorReason());
      }

      bufferIndex = 0;
    }
  }
}