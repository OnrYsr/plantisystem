#define VERSION "1.0.0"
#define BUILD_DATE __DATE__
#define BUILD_TIME __TIME__

#include <WiFi.h>
#include <ESPmDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

[... mevcut kodlar ...]

// Sistem durumu için yeni fonksiyon
void sendSystemMetrics() {
    StaticJsonDocument<500> doc;
    
    // Versiyon bilgisi
    doc["version"] = VERSION;
    doc["build_date"] = BUILD_DATE;
    doc["build_time"] = BUILD_TIME;
    
    // ESP32 metrikleri
    doc["esp32"]["cpu_freq"] = ESP.getCpuFreqMHz();
    doc["esp32"]["free_heap"] = ESP.getFreeHeap();
    doc["esp32"]["heap_size"] = ESP.getHeapSize();
    doc["esp32"]["flash_size"] = ESP.getFlashChipSize();
    doc["esp32"]["sdk_version"] = ESP.getSdkVersion();
    
    // WiFi metrikleri
    doc["wifi"]["rssi"] = WiFi.RSSI();
    doc["wifi"]["ip"] = WiFi.localIP().toString();
    doc["wifi"]["ssid"] = WiFi.SSID();
    
    // MQTT metrikleri
    doc["mqtt"]["connected"] = client.connected();
    doc["mqtt"]["server"] = mqtt_server;
    
    // Çalışma süresi
    doc["uptime_seconds"] = millis() / 1000;
    
    String systemData;
    serializeJson(doc, systemData);
    client.publish("system/metrics", systemData.c_str());
}

void loop() {
    ArduinoOTA.handle();
    
    [... mevcut loop kodu ...]
    
    // Her 30 saniyede bir sistem metriklerini gönder
    static unsigned long lastMetricsSend = 0;
    if (millis() - lastMetricsSend > 30000) {  // 30 saniye
        sendSystemMetrics();
        lastMetricsSend = millis();
    }
    
    delay(100);
}