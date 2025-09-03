import os
from dotenv import load_dotenv

# .env dosyasını yükle (varsa)
load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gizli-anahtar-buraya'
    
    # SQLite veritabanı
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///irrigation.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # MQTT ayarları
    MQTT_BROKER = os.environ.get('MQTT_BROKER') or 'localhost'
    MQTT_PORT = int(os.environ.get('MQTT_PORT') or 1883)
    MQTT_TOPICS = ['sensors/data', 'pump/status', 'system/status']
    
    # Uygulama ayarları
    DEBUG = os.environ.get('FLASK_DEBUG') or True
    HOST = os.environ.get('FLASK_HOST') or '0.0.0.0'
    PORT = int(os.environ.get('FLASK_PORT') or 5000)
