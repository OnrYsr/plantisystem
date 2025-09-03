import json
from datetime import datetime
from app import db, socketio
from app.models import SensorData, SystemLog

def handle_mqtt_message(app, msg):
    """MQTT mesajlarını işle ve veritabanına kaydet"""
    with app.app_context():
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            if topic == 'sensors/data':
                # Sensör verilerini kaydet
                sensor_data = SensorData(
                    timestamp=datetime.utcnow(),
                    temperature=payload.get('temperature'),
                    humidity=payload.get('humidity'),
                    soil_moisture_state=payload.get('soil_moisture', {}).get('state'),
                    soil_moisture_percent=payload.get('soil_moisture', {}).get('percent'),
                    light_raw=payload.get('light', {}).get('raw'),
                    light_percent=payload.get('light', {}).get('percent')
                )
                db.session.add(sensor_data)
                db.session.commit()
                
                # Socket.IO ile web arayüzüne gönder
                socketio.emit('sensor_update', {'topic': topic, 'payload': msg.payload.decode()})
            
            elif topic == 'system/status':
                # Sistem durumunu log'a kaydet
                log = SystemLog(
                    timestamp=datetime.utcnow(),
                    event_type='info',
                    message='System status update',
                    details=payload
                )
                db.session.add(log)
                db.session.commit()
                
                # Socket.IO ile web arayüzüne gönder
                socketio.emit('system_status', {'topic': topic, 'payload': msg.payload.decode()})
            
            elif topic == 'pump/status':
                # Pompa durumunu web arayüzüne gönder
                socketio.emit('pump_status', payload)
        
        except Exception as e:
            print(f"MQTT mesaj işleme hatası: {e}")
            # Hatayı log'a kaydet
            error_log = SystemLog(
                timestamp=datetime.utcnow(),
                event_type='error',
                message=f'MQTT message handling error: {str(e)}',
                details={'topic': msg.topic, 'payload': msg.payload.decode()}
            )
            db.session.add(error_log)
            db.session.commit()
