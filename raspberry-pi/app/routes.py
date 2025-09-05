from flask import jsonify, send_file
from app import app
from app.system_metrics import get_system_metrics
import cv2
import base64
import io

# Kamera fonksiyonları geçici olarak devre dışı bırakıldı
# Global kamera nesnesi ve durumu
# camera = None
# camera_error = None

# def init_camera():
#     global camera, camera_error
#     try:
#         if camera is None:
#             camera = cv2.VideoCapture(0)
#             if not camera.isOpened():
#                 camera_error = "Kamera başlatılamadı"
#                 return False
#             camera_error = None
#             return True
#         return camera.isOpened()
#     except Exception as e:
#         camera_error = str(e)
#         return False

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/sensors')
def get_sensors():
    return jsonify({
        "temperature": float(app.latest_sensor_data.get("temperature", 0)),
        "humidity": float(app.latest_sensor_data.get("humidity", 0)),
        "soil_moisture": {
            "state": app.latest_sensor_data.get("soil_moisture", {}).get("digital", "--"),
            "analog": int(app.latest_sensor_data.get("soil_moisture", {}).get("analog", 0)),
            "percent": int(app.latest_sensor_data.get("soil_moisture", {}).get("percent", 0))
        },
        "light": {
            "raw": int(app.latest_sensor_data.get("light", {}).get("raw", 0)),
            "percent": int(app.latest_sensor_data.get("light", {}).get("percent", 0))
        }
    })

@app.route('/api/camera/snapshot')
def get_snapshot():
    # Kamera fonksiyonu geçici olarak devre dışı
    return jsonify({'error': 'Kamera özelliği geçici olarak devre dışı bırakıldı'}), 400

@app.route('/api/system/metrics')
def system_metrics():
    return jsonify(get_system_metrics())

@app.route('/api/system/esp_metrics')
def esp_metrics():
    return jsonify(app.latest_esp_metrics if hasattr(app, 'latest_esp_metrics') else {})

@app.route('/api/pump/on', methods=['POST'])
def pump_on():
    app.mqtt_client.publish('pump/control', 'ON')
    return jsonify({"status": "success"})

@app.route('/api/pump/off', methods=['POST'])
def pump_off():
    app.mqtt_client.publish('pump/control', 'OFF')
    return jsonify({"status": "success"})