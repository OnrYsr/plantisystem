#!/bin/bash

# Gerekli Python paketlerini kur
echo "Python paketleri kuruluyor..."
pip install psutil

# Service dosyasını systemd dizinine kopyala
echo "Service dosyası kopyalanıyor..."
sudo cp plantisystem.service /etc/systemd/system/

# Service'i aktifleştir ve başlat
echo "Service aktifleştiriliyor..."
sudo systemctl daemon-reload
sudo systemctl enable plantisystem.service
sudo systemctl start plantisystem.service

# Service durumunu kontrol et
echo "Service durumu kontrol ediliyor..."
sudo systemctl status plantisystem.service

echo "Kurulum tamamlandı!"
echo "Log dosyasını görüntülemek için: journalctl -u plantisystem.service -f"