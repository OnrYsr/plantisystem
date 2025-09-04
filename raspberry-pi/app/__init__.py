from flask import Flask
import paho.mqtt.client as mqtt
import json

app = Flask(__name__, static_url_path='', static_folder='static')
app.latest_sensor_data = {}
app.latest_esp_metrics = {}

def on_connect(client, userdata, flags, rc):
    print(f"MQTT Bağlandı: {rc}")
    client.subscribe([
        ("sensors/data", 0),
        ("pump/status", 0),
        ("system/metrics", 0)  # ESP32 sistem metriklerini dinle
    ])
    print("MQTT topic'lere abone olundu")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"MQTT Mesajı alındı [{msg.topic}]: {msg.payload.decode()}")
        
        if msg.topic == "sensors/data":
            app.latest_sensor_data = payload
        elif msg.topic == "system/metrics":
            app.latest_esp_metrics = payload
            print("ESP32 metrikleri güncellendi:", payload)
    except Exception as e:
        print(f"MQTT mesaj işleme hatası: {e}")

# MQTT Client oluştur
app.mqtt_client = mqtt.Client()
app.mqtt_client.on_connect = on_connect
app.mqtt_client.on_message = on_message

# MQTT'ye bağlan
try:
    app.mqtt_client.connect("localhost", 1883, 60)
    app.mqtt_client.loop_start()
except Exception as e:
    print(f"MQTT bağlantı hatası: {e}")

from app import routes