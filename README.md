# 🌱 PlantiSystem - Akıllı Sulama Sistemi

## 📝 Proje Hakkında
PlantıSystem, bitkilerin sulama ihtiyaçlarını otomatik olarak takip eden ve yöneten akıllı bir sulama sistemidir. ESP32 mikrodenetleyici, çeşitli sensörler ve Raspberry Pi tabanlı bir web arayüzü kullanarak bitkilerin sağlığını izler ve optimal sulama koşullarını sağlar.

## 🔧 Sistem Bileşenleri

### Donanım
- ESP32 DevKit
- DHT11 Sıcaklık ve Nem Sensörü
- Toprak Nemi Sensörü (DO çıkışlı)
- LDR (Işık Sensörü)
- Su Pompası ve Röle Modülü
- OLED Ekran (SSD1306, I2C)
- Güç Kaynağı (5V)

### Yazılım
- ESP32 Arduino Kodu
- Raspberry Pi MQTT Broker (Mosquitto)
- Flask Web Arayüzü
- SQLite Veritabanı

## 📊 Sensör Verileri
- Sıcaklık (°C)
- Nem (%)
- Toprak Nemi (Kuru/Islak)
- Ortam Işığı (%)

## 🔌 Pin Bağlantıları
- DHT11 -> GPIO4
- Toprak Nemi (DO) -> GPIO32
- Su Pompası -> GPIO14
- Durum LED -> GPIO2 (Dahili LED)
- LDR -> GPIO33 (Analog)
- OLED -> I2C (SDA: GPIO21, SCL: GPIO22)

## 💻 Kurulum

### ESP32 Kurulumu
1. Arduino IDE'yi açın
2. Gerekli kütüphaneleri yükleyin (libraries_required.txt)
3. ESP32 kodunu yükleyin
4. Serial monitörden bağlantıyı kontrol edin

### Raspberry Pi Kurulumu
1. Mosquitto MQTT Broker kurulumu:
```bash
sudo apt update
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable mosquitto
```

2. Python sanal ortam ve bağımlılıklar:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Flask uygulamasını başlatın:
```bash
python run.py
```

## 🛠️ Kontrol Komutları

### Serial Monitor Komutları
- `1`: Pompayı aç
- `0`: Pompayı kapat
- `h`: LDR maksimum ışık kalibrasyonu
- `l`: LDR minimum ışık kalibrasyonu
- `c`: LDR kalibrasyon durumu

### MQTT Topic'leri
- `sensors/data`: Sensör verileri
- `pump/control`: Pompa kontrolü (ON/OFF)
- `pump/status`: Pompa durumu
- `system/status`: Sistem durumu
- `system/command`: Sistem komutları

## 📱 Web Arayüzü
- Adres: `http://<raspberry-pi-ip>:5000`
- Varsayılan kullanıcı: `admin`
- Varsayılan şifre: `sifre123`

## 🔄 Veri Akışı
1. ESP32 sensör verilerini okur
2. Veriler MQTT üzerinden Raspberry Pi'ye gönderilir
3. Flask uygulaması verileri alır ve veritabanına kaydeder
4. Web arayüzü gerçek zamanlı olarak güncellenir
5. Kullanıcı web arayüzünden pompayı kontrol edebilir

## 📊 Veritabanı Şeması
- Users: Kullanıcı bilgileri
- SensorData: Sensör verileri geçmişi
- PumpLog: Pompa çalışma geçmişi

## 🔒 Güvenlik
- Web arayüzü için kullanıcı kimlik doğrulaması
- MQTT bağlantısı için güvenli ağ yapılandırması
- Düzenli yedekleme önerisi

## 🐛 Sorun Giderme
1. ESP32 bağlantı sorunları:
   - WiFi sinyalini kontrol edin
   - MQTT broker IP adresini doğrulayın
   - Serial monitörden hata mesajlarını kontrol edin

2. Sensör sorunları:
   - Bağlantıları kontrol edin
   - Kalibrasyon yapın
   - Güç kaynağını kontrol edin

3. Web arayüzü sorunları:
   - Flask uygulamasının çalıştığını kontrol edin
   - Port çakışmalarını kontrol edin
   - Log dosyalarını inceleyin
