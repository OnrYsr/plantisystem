from flask import Flask
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
from config import Config

# Flask eklentileri
socketio = SocketIO()

# MQTT client
mqtt_client = mqtt.Client()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # SocketIO başlat
    socketio.init_app(app)

    # Blueprint'leri kaydet
    from app.routes import main
    app.register_blueprint(main)

    # MQTT callbacks
    def on_connect(client, userdata, flags, rc):
        print(f"MQTT Bağlandı: {rc}")
        for topic in app.config['MQTT_TOPICS']:
            client.subscribe(topic)

    def on_message(client, userdata, msg):
        try:
            # Socket.IO ile web arayüzüne gönder
            socketio.emit('sensor_update', {
                'topic': msg.topic,
                'payload': msg.payload.decode()
            })
        except Exception as e:
            print(f"MQTT mesaj işleme hatası: {e}")

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    # MQTT bağlantısı
    try:
        mqtt_client.connect(app.config['MQTT_BROKER'], app.config['MQTT_PORT'], 60)
        mqtt_client.loop_start()
        print("MQTT broker'a bağlandı")
    except Exception as e:
        print(f"MQTT bağlantı hatası: {e}")

    return app