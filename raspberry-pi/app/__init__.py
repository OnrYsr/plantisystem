from flask import Flask
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
from config import Config
import json
import uuid

print("Flask uygulaması başlatılıyor...")

# Flask eklentileri
socketio = SocketIO(cors_allowed_origins="*")

# MQTT client - benzersiz ID ile
client_id = f'flask_client_{str(uuid.uuid4())}'
mqtt_client = mqtt.Client(client_id=client_id, clean_session=True)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    print(f"MQTT Broker: {app.config['MQTT_BROKER']}")
    print(f"MQTT Port: {app.config['MQTT_PORT']}")
    print(f"MQTT Client ID: {client_id}")

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
        if rc != 0:
            print(f"❌ MQTT Bağlantısı beklenmedik şekilde kesildi, rc: {rc}")
            print("🔄 5 saniye içinde yeniden bağlanmaya çalışılacak...")

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
            
            # Doğrudan JSON objesini gönder
            if msg.topic == 'sensors/data':
                socketio.emit('sensor_update', {
                    'topic': msg.topic,
                    'payload': payload
                })
            elif msg.topic == 'pump/status':
                socketio.emit('pump_status', payload)
            elif msg.topic == 'system/status':
                socketio.emit('system_status', payload)
                
            print("  ✅ Veri web arayüzüne gönderildi")
            
        except json.JSONDecodeError as e:
            print(f"  ❌ JSON parse hatası: {e}")
        except Exception as e:
            print(f"  ❌ Genel hata: {e}")
            print(f"  Stack trace: {str(e.__traceback__)}")

    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_message = on_message

    # MQTT bağlantı ayarları
    mqtt_client.reconnect_delay_set(min_delay=1, max_delay=5)  # Yeniden bağlanma gecikmesi
    mqtt_client.username_pw_set(username="", password="")  # Anonim bağlantı

    # MQTT bağlantısı
    try:
        print("\n🔌 MQTT Broker'a bağlanılıyor...")
        mqtt_client.connect(app.config['MQTT_BROKER'], app.config['MQTT_PORT'], keepalive=60)
        mqtt_client.loop_start()
    except Exception as e:
        print(f"❌ MQTT bağlantı hatası: {e}")

    return app