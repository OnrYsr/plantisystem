from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
from config import Config

# Flask eklentileri
db = SQLAlchemy()
socketio = SocketIO()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# MQTT client
mqtt_client = mqtt.Client()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Eklentileri başlat
    db.init_app(app)
    socketio.init_app(app)
    login_manager.init_app(app)

    # Blueprint'leri kaydet
    from app.routes import main, auth
    app.register_blueprint(main)
    app.register_blueprint(auth)

    # MQTT callbacks
    def on_connect(client, userdata, flags, rc):
        print(f"MQTT Bağlandı: {rc}")
        for topic in app.config['MQTT_TOPICS']:
            client.subscribe(topic)

    def on_message(client, userdata, msg):
        from app.mqtt_handlers import handle_mqtt_message
        handle_mqtt_message(app, msg)

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    # MQTT bağlantısı
    with app.app_context():
        try:
            mqtt_client.connect(app.config['MQTT_BROKER'], app.config['MQTT_PORT'], 60)
            mqtt_client.loop_start()
            print("MQTT broker'a bağlandı")
        except Exception as e:
            print(f"MQTT bağlantı hatası: {e}")

        # Veritabanını oluştur
        db.create_all()

        # İlk kullanıcıyı oluştur
        from app.models import User
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.set_password('sifre123')
            db.session.add(admin)
            db.session.commit()

    return app
