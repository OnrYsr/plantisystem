import psutil
import os
import json
from datetime import datetime

def get_system_metrics():
    metrics = {
        "timestamp": datetime.now().isoformat(),
        
        # CPU metrikleri
        "cpu": {
            "percent": psutil.cpu_percent(),
            "temperature": psutil.sensors_temperatures().get('cpu_thermal', [{'current': 0}])[0].current,
            "frequency": psutil.cpu_freq().current
        },
        
        # RAM metrikleri
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent": psutil.virtual_memory().percent
        },
        
        # Disk metrikleri
        "disk": {
            "total": psutil.disk_usage('/').total,
            "free": psutil.disk_usage('/').free,
            "percent": psutil.disk_usage('/').percent
        },
        
        # Network metrikleri
        "network": {
            "bytes_sent": psutil.net_io_counters().bytes_sent,
            "bytes_recv": psutil.net_io_counters().bytes_recv
        },
        
        # Sistem bilgileri
        "uptime": int(psutil.boot_time()),
        "process_count": len(psutil.pids())
    }
    
    return metrics

def get_mqtt_metrics(mqtt_client):
    return {
        "connected": mqtt_client.is_connected(),
        "client_count": len(mqtt_client._client_id),  # Bağlı client sayısı
        "messages_received": mqtt_client._messages_received,  # Alınan mesaj sayısı
    }
