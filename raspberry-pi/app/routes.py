from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db, mqtt_client
from app.models import User, SensorData, PumpLog, SystemLog
from datetime import datetime, timedelta

# Blueprint'ler
main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)

# Ana sayfa
@main.route('/')
@login_required
def index():
    return render_template('index.html')

# Sensör verileri API
@main.route('/api/sensors/latest')
@login_required
def get_latest_sensor_data():
    data = SensorData.query.order_by(SensorData.timestamp.desc()).first()
    return jsonify(data.to_dict() if data else {})

@main.route('/api/sensors/history')
@login_required
def get_sensor_history():
    hours = request.args.get('hours', 24, type=int)
    since = datetime.utcnow() - timedelta(hours=hours)
    
    data = SensorData.query.filter(
        SensorData.timestamp >= since
    ).order_by(SensorData.timestamp.asc()).all()
    
    return jsonify([d.to_dict() for d in data])

# Pompa kontrolü
@main.route('/api/pump/on')
@login_required
def pump_on():
    mqtt_client.publish('pump/control', 'ON')
    
    # Log kaydı
    log = PumpLog(
        triggered_by=current_user.username,
        user_id=current_user.id,
        is_manual=True
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Pump turned ON'})

@main.route('/api/pump/off')
@login_required
def pump_off():
    mqtt_client.publish('pump/control', 'OFF')
    
    # Son açık log kaydını güncelle
    log = PumpLog.query.filter_by(
        triggered_by=current_user.username,
        end_time=None
    ).order_by(PumpLog.start_time.desc()).first()
    
    if log:
        log.end_time = datetime.utcnow()
        log.duration = (log.end_time - log.start_time).seconds
        db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Pump turned OFF'})

# Pompa geçmişi
@main.route('/api/pump/history')
@login_required
def get_pump_history():
    days = request.args.get('days', 7, type=int)
    since = datetime.utcnow() - timedelta(days=days)
    
    logs = PumpLog.query.filter(
        PumpLog.start_time >= since
    ).order_by(PumpLog.start_time.desc()).all()
    
    return jsonify([log.to_dict() for log in logs])

# Sistem logları
@main.route('/api/system/logs')
@login_required
def get_system_logs():
    hours = request.args.get('hours', 24, type=int)
    since = datetime.utcnow() - timedelta(hours=hours)
    
    logs = SystemLog.query.filter(
        SystemLog.timestamp >= since
    ).order_by(SystemLog.timestamp.desc()).all()
    
    return jsonify([log.to_dict() for log in logs])

# Kimlik doğrulama
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
            
        flash('Geçersiz kullanıcı adı veya şifre')
    
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
