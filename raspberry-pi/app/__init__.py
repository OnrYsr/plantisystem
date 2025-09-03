from flask import Flask
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
import json

print("Flask uygulaması başlatılıyor...")

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
        client.subscribe("pump/status")
        print("MQTT topic'lerine abone olundu")

    def on_message(client, userdata, msg):
        print(f"\nMQTT Mesajı alındı - Topic: {msg.topic}")
        print(f"Payload: {msg.payload.decode()}")
        
        try:
            # JSON parse et
            payload = json.loads(msg.payload.decode())
            
            # Socket.IO ile gönder
            print("Socket.IO ile gönderiliyor...")
            socketio.emit('sensor_update', payload)
            print("Veri gönderildi")
            
        except Exception as e:
            print(f"Hata: {e}")

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    # MQTT bağlantısı
    try:
        mqtt_client.connect("localhost", 1883, 60)
        mqtt_client.loop_start()
        print("MQTT broker'a bağlandı")
    except Exception as e:
        print(f"MQTT bağlantı hatası: {e}")

    return app