import psutil
import os
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
        }
    }
    
    return metrics