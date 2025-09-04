from flask import jsonify
from app import app
from app.system_metrics import get_system_metrics

@app.route('/api/system/metrics')
def system_metrics():
    return jsonify(get_system_metrics())