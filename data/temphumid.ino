#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <time.h>

// =====================
// User Configuration
// =====================
const char* WIFI_SSID = "net";
const char* WIFI_PASSWORD = "12345678";

// MQTT config
const char* MQTT_BROKER = "iot.cpe.ku.ac.th";
const int   MQTT_PORT   = 1883;
const char* MQTT_TOPIC  = "b6710545881/urbansense/data";
const char* MQTT_USER   = "b6710545881";
const char* MQTT_PASS   = "watcharapat.p@ku.th";

// Device info
const char* DEVICE_ID  = "kidbright-esp32-01";
const char* STATION_ID = "BTS-XXX";
const char* FW_VERSION = "0.1.0";

// Sensor config
#define DHT_PIN 33
#define DHT_TYPE DHT22

// Sampling (1 minute)
const unsigned long SAMPLE_INTERVAL_MS = 60000;

// =====================
// Globals
// =====================
DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastSampleMs = 0;

// =====================
// Helper Functions
// =====================
bool isRushHour(int hour24) {
  return ((hour24 >= 7 && hour24 < 9) || (hour24 >= 16 && hour24 < 19));
}

String buildTimestamp() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    return "1970-01-01T00:00:00+07:00";
  }
  char buf[30];
  strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%S+07:00", &timeinfo);
  return String(buf);
}

// =====================
// WiFi
// =====================
void connectWifi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("Connecting WiFi");
  int retry = 0;

  while (WiFi.status() != WL_CONNECTED && retry < 20) {
    delay(500);
    Serial.print(".");
    retry++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi FAILED");
  }
}

// =====================
// MQTT
// =====================
void connectMQTT() {
  client.setServer(MQTT_BROKER, MQTT_PORT);

  while (!client.connected()) {
    Serial.print("Connecting MQTT...");

    if (client.connect("esp32-urbansense", MQTT_USER, MQTT_PASS)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retry in 2s");
      delay(2000);
    }
  }
}

// =====================
// Publish Function
// =====================
void publishReading(float temperatureC, float humidityPct, bool rushHour) {

  if (WiFi.status() != WL_CONNECTED) {
    connectWifi();
  }

  if (!client.connected()) {
    connectMQTT();
  }

  StaticJsonDocument<256> doc;
  doc["device_id"] = DEVICE_ID;
  doc["station_id"] = STATION_ID;
  doc["timestamp"] = buildTimestamp();
  doc["temperature_c"] = temperatureC;
  doc["humidity_pct"] = humidityPct;
  doc["is_rush_hour"] = rushHour;
  doc["firmware_version"] = FW_VERSION;

  char payload[256];
  serializeJson(doc, payload);

  Serial.print("Publishing: ");
  Serial.println(payload);

  if (client.publish(MQTT_TOPIC, payload)) {
    Serial.println("Publish success");
  } else {
    Serial.println("Publish FAILED");
  }
}

// =====================
// Setup
// =====================
void setup() {
  Serial.begin(115200);
  delay(2000);

  dht.begin();
  connectWifi();

  // Time sync
  configTime(7 * 3600, 0, "pool.ntp.org", "time.nist.gov");

  Serial.print("Waiting for NTP");
  struct tm timeinfo;
  while (!getLocalTime(&timeinfo)) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nTime synced!");

  connectMQTT();
}

// =====================
// Loop
// =====================
void loop() {

  client.loop(); // keep MQTT alive

  unsigned long now = millis();
  if (now - lastSampleMs < SAMPLE_INTERVAL_MS) {
    delay(100);
    return;
  }
  lastSampleMs = now;

  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("DHT read failed");
    return;
  }

  struct tm timeinfo;
  getLocalTime(&timeinfo);
  bool rushHour = isRushHour(timeinfo.tm_hour);

  Serial.print("T=");
  Serial.print(temperature);
  Serial.print("C H=");
  Serial.print(humidity);
  Serial.print("% Rush=");
  Serial.println(rushHour ? "YES" : "NO");

  publishReading(temperature, humidity, rushHour);
}