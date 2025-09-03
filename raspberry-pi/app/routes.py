from flask import Blueprint, render_template, jsonify
from app import mqtt_client

# Blueprint
main = Blueprint('main', __name__)

# Ana sayfa
@main.route('/')
def index():
    return render_template('index.html')

# Pompa kontrolü
@main.route('/api/pump/on')
def pump_on():
    mqtt_client.publish('pump/control', 'ON')
    return jsonify({'status': 'success', 'message': 'Pump turned ON'})

@main.route('/api/pump/off')
def pump_off():
    mqtt_client.publish('pump/control', 'OFF')
    return jsonify({'status': 'success', 'message': 'Pump turned OFF'})