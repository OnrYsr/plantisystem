#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// WiFi ayarları
const char* ssid = "Zyxel_3691";               
const char* password = "3883D488Y7";         
const char* mqtt_server = "192.168.1.7";      // Raspberry Pi IP adresi

// Pin tanımlamaları
const int STATUS_LED_PIN = 2;     // Durum LED'i (GPIO2) - Dahili mavi LED - WiFi/MQTT durumu
const int DHT_PIN = 4;            // DHT11 sensörü (GPIO4)
const int PUMP_PIN = 14;          // Su pompası kontrolü (GPIO14)
const int MOISTURE_PIN = 32;      // Toprak nem sensörü DO pini (GPIO32)
const int LDR_PIN = 33;          // LDR sensörü analog pini (GPIO33)

// OLED ekran ayarları
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3C
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// DHT11 sensör nesnesi
#define DHTTYPE DHT11
DHT dht(DHT_PIN, DHTTYPE);

// MQTT client
WiFiClient espClient;
PubSubClient client(espClient);

// Değişkenler
bool pumpState = false;          // Su pompası durumu
float temperature = 0;           // Sıcaklık değeri
float humidity = 0;             // Hava nemi değeri
bool moistureRaw = false;       // Toprak nem sensörü ham değer (true: kuru, false: ıslak)
int moisturePercent = 0;        // Toprak nem yüzdesi (0: kuru, 100: ıslak)
int lightRaw = 0;              // LDR ham değer (0-4095)
int lightPercent = 0;          // LDR yüzde değeri (0: karanlık, 100: aydınlık)
int lightMin = 4095;           // Kalibrasyon minimum değeri (karanlık)
int lightMax = 0;             // Kalibrasyon maximum değeri (aydınlık)

unsigned long lastStatusSend = 0;
unsigned long lastSensorRead = 0;
const unsigned long STATUS_INTERVAL = 10000;  // 10 saniye
const unsigned long SENSOR_INTERVAL = 5000;   // 5 saniye

void setup() {
  Serial.begin(115200);
  
  // I2C başlat
  Wire.begin();
  
  // OLED ekranı başlat
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println("SSD1306 allocation failed");
    for(;;); // Don't proceed, loop forever
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.display();
  
  // Pin modları
  pinMode(STATUS_LED_PIN, OUTPUT);
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(MOISTURE_PIN, INPUT);  // Dijital giriş olarak ayarla
  pinMode(LDR_PIN, INPUT);      // LDR için analog giriş
  
  // Başlangıç durumu
  digitalWrite(STATUS_LED_PIN, LOW);
  digitalWrite(PUMP_PIN, LOW);
  
  // DHT11 başlat
  dht.begin();
  
  Serial.println("🚀 ESP32 Akıllı Sulama Sistemi Başlatılıyor...");
  Serial.println("🔵 Mavi LED: Bağlantı durumu (GPIO2)");
  Serial.printf("DHT11 Pin: %d\n", DHT_PIN);
  Serial.printf("Pump Pin: %d\n", PUMP_PIN);
  Serial.printf("Moisture Pin: %d\n", MOISTURE_PIN);
  
  // Sistem başlangıç LED gösterisi
  for (int i = 0; i < 3; i++) {
    digitalWrite(STATUS_LED_PIN, HIGH);
    delay(200);
    digitalWrite(STATUS_LED_PIN, LOW);
    delay(200);
  }
  
  // Pump test
  Serial.println("🚰 Pump test başlıyor...");
  digitalWrite(PUMP_PIN, HIGH);
  delay(1000);
  digitalWrite(PUMP_PIN, LOW);
  Serial.println("✅ Pump test tamamlandı.");
  
  // Sensör test
  Serial.println("🌡️ Sensör testi başlıyor...");
  readSensors();
  Serial.printf("Sıcaklık: %.1f°C, Nem: %.1f%%, Toprak: %s\n", 
    temperature, humidity, moistureRaw ? "KURU" : "ISLAK");
  Serial.println("✅ Sensör testi tamamlandı.");
  
  // WiFi bağlantısı
  setupWiFi();
  
  // MQTT ayarları
  client.setServer(mqtt_server, 1883);
  client.setCallback(onMqttMessage);
  
  Serial.println("🎯 Sistem hazır!");
}

void setupWiFi() {
  WiFi.begin(ssid, password);
  Serial.print("📡 WiFi'ye bağlanıyor");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    digitalWrite(STATUS_LED_PIN, !digitalRead(STATUS_LED_PIN));
  }
  
  Serial.println();
  Serial.print("✅ WiFi bağlandı! IP: ");
  Serial.println(WiFi.localIP());
  
  digitalWrite(STATUS_LED_PIN, HIGH);
}

void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  Serial.printf("MQTT Mesajı alındı [%s]: %s\n", topic, message.c_str());
  
  // Su pompası kontrolü
  if (String(topic) == "pump/control") {
    if (message == "ON" || message == "1") {
      controlPump(true);
    } else if (message == "OFF" || message == "0") {
      controlPump(false);
    }
  }
  
  // Sistem komutları
  if (String(topic) == "system/command") {
    if (message == "status") {
      sendSystemStatus();
    } else if (message == "restart") {
      ESP.restart();
    }
  }
}

void controlPump(bool state) {
  pumpState = state;
  digitalWrite(PUMP_PIN, state ? HIGH : LOW);
  
  String status = state ? "ON" : "OFF";
  Serial.printf("🚰 Pump (GPIO%d): %s\n", PUMP_PIN, status.c_str());
  
  client.publish("pump/status", status.c_str());
}

void readSensors() {
  // DHT11 okuma
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();
  
  // Toprak nemi dijital okuma (true: kuru, false: ıslak)
  moistureRaw = digitalRead(MOISTURE_PIN);
  moisturePercent = moistureRaw ? 0 : 100;  // Tersine çevir: false->100% (ıslak), true->0% (kuru)
  
  // LDR analog okuma
  lightRaw = analogRead(LDR_PIN);  // 0-4095 arası değer
  lightPercent = map(lightRaw, lightMin, lightMax, 0, 100);  // Kalibre edilmiş değerlere göre yüzde hesapla
  lightPercent = constrain(lightPercent, 0, 100);  // 0-100 arasına sınırla
  
  // NaN kontrolü
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("❌ DHT11 okuma hatası!");
    temperature = 0;
    humidity = 0;
  }
}

void updateDisplay() {
  display.clearDisplay();
  
  // Başlık
  display.setTextSize(1);
  display.setCursor(0,0);
  display.println("Akilli Sulama Sistemi");
  display.drawLine(0, 9, display.width(), 9, SSD1306_WHITE);
  
  // Sıcaklık ve Nem
  display.setCursor(0, 12);
  display.printf("Sicaklik: %.1f C", temperature);
  display.setCursor(0, 22);
  display.printf("Nem: %.1f%%", humidity);
  
  // Toprak Nemi
  display.setCursor(0, 32);
  display.printf("Toprak: %s", moistureRaw ? "KURU" : "ISLAK");
  
  // Işık Durumu
  display.setCursor(0, 42);
  display.printf("Isik: %d%%", lightPercent);
  
  // Pompa Durumu
  display.setCursor(0, 52);
  display.printf("Pompa: %s", pumpState ? "ACIK" : "KAPALI");
  
  display.display();
}

void sendSensorData() {
  StaticJsonDocument<300> doc;
  doc["device"] = "ESP32_Smart_Irrigation";
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["soil_moisture"]["state"] = moistureRaw ? "KURU" : "ISLAK";
  doc["soil_moisture"]["percent"] = moisturePercent;
  doc["light"]["raw"] = lightRaw;
  doc["light"]["percent"] = lightPercent;
  doc["timestamp"] = millis();
  
  String sensorData;
  serializeJson(doc, sensorData);
  
  client.publish("sensors/data", sensorData.c_str());
  
  Serial.printf("📊 Sensör verileri: %.1f°C, %.1f%%, Toprak:%s, Işık:%d%% (ham:%d)\n", 
    temperature, humidity, moistureRaw ? "KURU" : "ISLAK", lightPercent, lightRaw);
}

void sendSystemStatus() {
  StaticJsonDocument<400> doc;
  doc["device"] = "ESP32_Smart_Irrigation";
  doc["wifi_signal"] = WiFi.RSSI();
  doc["free_heap"] = ESP.getFreeHeap();
  doc["uptime"] = millis();
  doc["pump_state"] = pumpState;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["soil_moisture_state"] = moistureRaw ? "KURU" : "ISLAK";
  doc["soil_moisture_percent"] = moisturePercent;
  doc["light"]["raw"] = lightRaw;
  doc["light"]["percent"] = lightPercent;
  doc["status_led"] = digitalRead(STATUS_LED_PIN) ? "CONNECTED" : "DISCONNECTED";
  doc["timestamp"] = millis();
  
  String statusData;
  serializeJson(doc, statusData);
  
  client.publish("system/status", statusData.c_str());
  
  Serial.printf("📊 Sistem durumu: Pump=%s, WiFi=%ddBm, %.1f°C, %.1f%%, Toprak=%s, Status=🔵%s\n", 
    pumpState ? "ON" : "OFF",
    WiFi.RSSI(),
    temperature, humidity,
    moistureRaw ? "KURU" : "ISLAK",
    digitalRead(STATUS_LED_PIN) ? "CONNECTED" : "DISCONNECTED"
  );
}

void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("📡 MQTT'ye bağlanıyor...");
    
    // MQTT bağlantısı sırasında mavi LED yanıp sönsün
    for (int i = 0; i < 5; i++) {
      digitalWrite(STATUS_LED_PIN, HIGH);
      delay(100);
      digitalWrite(STATUS_LED_PIN, LOW);
      delay(100);
    }
    
    if (client.connect("ESP32SmartIrrigation")) {
      Serial.println("✅ MQTT bağlandı!");
      
      digitalWrite(STATUS_LED_PIN, HIGH);
      
      // Topic'lere abone ol
      client.subscribe("pump/control");
      client.subscribe("system/command");
      
      client.publish("system/status", "ESP32 Smart Irrigation Connected");
      sendSystemStatus();
      
      Serial.println("📡 MQTT topic'lerine abone olundu");
      
    } else {
      Serial.printf("❌ MQTT bağlantı hatası, rc=%d\n", client.state());
      Serial.println("🔵 5 saniye sonra tekrar denenecek...");
      
      digitalWrite(STATUS_LED_PIN, LOW);
      delay(5000);
    }
  }
}

void loop() {
  // Serial'den komut kontrolü
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == '1') {
      controlPump(true);
      Serial.println("🚰 Pompa AÇILDI");
    }
    else if (cmd == '0') {
      controlPump(false);
      Serial.println("🚰 Pompa KAPATILDI");
    }
    // LDR Kalibrasyon komutları
    else if (cmd == 'h') {  // high - maksimum ışık
      lightMax = lightRaw;
      Serial.printf("📊 Maksimum ışık değeri ayarlandı: %d\n", lightMax);
    }
    else if (cmd == 'l') {  // low - minimum ışık
      lightMin = lightRaw;
      Serial.printf("📊 Minimum ışık değeri ayarlandı: %d\n", lightMin);
    }
    else if (cmd == 'c') {  // calibration status
      Serial.printf("📊 Kalibrasyon değerleri - Min: %d, Max: %d\n", lightMin, lightMax);
    }
  }

  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();
  
  // Periyodik sensör okuma (5 saniyede bir)
  if (millis() - lastSensorRead > SENSOR_INTERVAL) {
    readSensors();
    sendSensorData();
    updateDisplay();  // OLED ekranı güncelle
    lastSensorRead = millis();
  }
  
  // Periyodik durum gönderimi (10 saniyede bir)
  if (millis() - lastStatusSend > STATUS_INTERVAL) {
    sendSystemStatus();
    lastStatusSend = millis();
  }
  
  delay(100);
}
