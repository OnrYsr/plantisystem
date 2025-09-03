from flask import Flask, jsonify
import paho.mqtt.client as mqtt
import json

# Global değişken olarak son sensör verilerini tutalım
latest_sensor_data = {
    'temperature': 0,
    'humidity': 0,
    'soil_moisture': {'state': '--', 'percent': 0},
    'light': {'raw': 0, 'percent': 0}
}

def create_app():
    app = Flask(__name__)

    # MQTT callbacks
    def on_connect(client, userdata, flags, rc):
        print(f"MQTT Bağlandı: {rc}")
        client.subscribe("sensors/data")
        client.subscribe("pump/status")
        print("MQTT topic'lere abone olundu")

    def on_message(client, userdata, msg):
        global latest_sensor_data
        print(f"MQTT Mesajı alındı: {msg.payload.decode()}")
        
        if msg.topic == "sensors/data":
            latest_sensor_data = json.loads(msg.payload.decode())

    # MQTT client
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    # MQTT bağlantısı
    mqtt_client.connect("localhost", 1883, 60)
    mqtt_client.loop_start()

    # API endpoint'leri
    @app.route('/api/sensors')
    def get_sensors():
        return jsonify(latest_sensor_data)

    @app.route('/api/pump/on')
    def pump_on():
        mqtt_client.publish('pump/control', 'ON')
        return jsonify({'status': 'success', 'message': 'Pump turned ON'})

    @app.route('/api/pump/off')
    def pump_off():
        mqtt_client.publish('pump/control', 'OFF')
        return jsonify({'status': 'success', 'message': 'Pump turned OFF'})

    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    return app