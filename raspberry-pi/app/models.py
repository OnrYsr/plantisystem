from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    pump_logs = db.relationship('PumpLog', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    soil_moisture_state = db.Column(db.String(10))
    soil_moisture_percent = db.Column(db.Integer)
    light_raw = db.Column(db.Integer)
    light_percent = db.Column(db.Integer)

    def to_dict(self):
        return {
            'timestamp': self.timestamp.isoformat(),
            'temperature': self.temperature,
            'humidity': self.humidity,
            'soil_moisture': {
                'state': self.soil_moisture_state,
                'percent': self.soil_moisture_percent
            },
            'light': {
                'raw': self.light_raw,
                'percent': self.light_percent
            }
        }

class PumpLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # süre (saniye)
    triggered_by = db.Column(db.String(80))  # kullanıcı adı veya "auto"
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_manual = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'triggered_by': self.triggered_by,
            'is_manual': self.is_manual
        }

class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    event_type = db.Column(db.String(50))  # 'info', 'warning', 'error'
    message = db.Column(db.String(500))
    details = db.Column(db.JSON)

    def to_dict(self):
        return {
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'message': self.message,
            'details': self.details
        }
