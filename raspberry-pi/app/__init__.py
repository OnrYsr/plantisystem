from flask import Flask
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
import json

# Flask eklentileri
socketio = SocketIO()

# MQTT client
mqtt_client = mqtt.Client()

def create_app():
    app = Flask(__name__)
    
    # SocketIO başlat
    socketio.init_app(app)

    # Blueprint'leri kaydet
    from app.routes import main
    app.register_blueprint(main)

    # MQTT callbacks
    def on_connect(client, userdata, flags, rc):
        print(f"MQTT Bağlandı: {rc}")
        client.subscribe("sensors/data")
        print("MQTT topic'e abone olundu")

    def on_message(client, userdata, msg):
        print(f"MQTT Mesajı alındı: {msg.payload.decode()}")
        socketio.emit('sensor_data', msg.payload.decode())

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    # MQTT bağlantısı
    mqtt_client.connect("localhost", 1883, 60)
    mqtt_client.loop_start()

    return app