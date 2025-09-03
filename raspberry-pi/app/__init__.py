from flask import Flask
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
from config import Config
import json

print("Flask uygulaması başlatılıyor...")

# Flask eklentileri
socketio = SocketIO(cors_allowed_origins="*")

# MQTT client
mqtt_client = mqtt.Client(client_id="flask_client")

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    print(f"MQTT Broker: {app.config['MQTT_BROKER']}")
    print(f"MQTT Port: {app.config['MQTT_PORT']}")
    print(f"MQTT Topics: {app.config['MQTT_TOPICS']}")

    # SocketIO başlat
    socketio.init_app(app)

    # Blueprint'leri kaydet
    from app.routes import main
    app.register_blueprint(main)

    # MQTT callbacks
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("✅ MQTT Broker'a başarıyla bağlandı")
            # Topic'lere abone ol
            for topic in app.config['MQTT_TOPICS']:
                client.subscribe(topic)
                print(f"  📌 Topic'e abone olundu: {topic}")
        else:
            print(f"❌ MQTT Bağlantı hatası, rc: {rc}")

    def on_disconnect(client, userdata, rc):
        print(f"❌ MQTT Bağlantısı kesildi, rc: {rc}")
        if rc != 0:
            print("🔄 Yeniden bağlanmaya çalışılacak...")

    def on_message(client, userdata, msg):
        try:
            print(f"\n📨 MQTT Mesajı alındı:")
            print(f"  Topic: {msg.topic}")
            payload_str = msg.payload.decode()
            print(f"  Raw Payload: {payload_str}")
            
            # JSON parse et
            payload = json.loads(payload_str)
            print(f"  Parsed JSON: {json.dumps(payload, indent=2)}")
            
            # Socket.IO ile gönder
            print("  🔄 Socket.IO ile web arayüzüne gönderiliyor...")
            socketio.emit('sensor_update', {
                'topic': msg.topic,
                'payload': payload
            })
            print("  ✅ Veri web arayüzüne gönderildi")
            
        except json.JSONDecodeError as e:
            print(f"  ❌ JSON parse hatası: {e}")
        except Exception as e:
            print(f"  ❌ Genel hata: {e}")

    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_message = on_message

    # MQTT bağlantısı
    try:
        print("\n🔌 MQTT Broker'a bağlanılıyor...")
        mqtt_client.connect(app.config['MQTT_BROKER'], app.config['MQTT_PORT'], 60)
        mqtt_client.loop_start()
    except Exception as e:
        print(f"❌ MQTT bağlantı hatası: {e}")

    return app