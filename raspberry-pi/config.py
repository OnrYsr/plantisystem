import os
from dotenv import load_dotenv

# .env dosyasını yükle (varsa)
load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gizli-anahtar-buraya'
    
    # MQTT ayarları
    MQTT_BROKER = 'localhost'  # Doğrudan localhost kullan
    MQTT_PORT = 1883
    MQTT_TOPICS = ['sensors/data', 'pump/status', 'system/status']
    
    # Uygulama ayarları
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000