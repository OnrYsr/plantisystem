from flask import jsonify
from app import app
from app.system_metrics import get_system_metrics

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/sensors')
def get_sensors():
    print("Debug - latest_sensor_data:", app.latest_sensor_data)
    return jsonify({
        "temperature": float(app.latest_sensor_data.get("temperature", 0)),
        "humidity": float(app.latest_sensor_data.get("humidity", 0)),
        "soil_moisture": {
            "state": app.latest_sensor_data.get("soil_moisture", {}).get("digital"),
            "analog": int(app.latest_sensor_data.get("soil_moisture", {}).get("analog", 0)),
            "percent": int(app.latest_sensor_data.get("soil_moisture", {}).get("percent", 0))
        },
        "light": {
            "raw": int(app.latest_sensor_data.get("light", {}).get("raw", 0)),
            "percent": int(app.latest_sensor_data.get("light", {}).get("percent", 0))
        }
    })

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