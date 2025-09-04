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
        ("system/metrics", 0)
    ])
    print("MQTT topic'lere abone olundu")

def on_message(client, userdata, msg):
    try:
        if msg.topic == "sensors/data":
            app.latest_sensor_data = json.loads(msg.payload.decode())
        elif msg.topic == "system/metrics":
            app.latest_esp_metrics = json.loads(msg.payload.decode())
        print(f"MQTT Mesajı alındı: {msg.payload.decode()}")
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