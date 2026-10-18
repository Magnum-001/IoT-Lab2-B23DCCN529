import json
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# ================= CẤU HÌNH INFLUXDB =================
INFLUX_URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUX_TOKEN = "OJ-0mr90axwEmHyEDyGgg07k7fVYpsOCf-PdPkAksMiHYm9yrEH04FzjC1P8Fve2cZ3mfuIR8dxhBdkedStytA=="
INFLUX_ORG = "Magnum"
INFLUX_BUCKET = "sensor"

# Khởi tạo InfluxDB Client
influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# ================= CẤU HÌNH MQTT =================
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "ptit/b23dccn529/sensors"

# Hàm xử lý khi kết nối MQTT thành công
def on_connect(client, userdata, flags, rc):
    print(f"Đã kết nối với MQTT Broker (Mã trạng thái: {rc})")
    client.subscribe(MQTT_TOPIC)
    print(f"Đang lắng nghe dữ liệu tại topic: {MQTT_TOPIC}")

# Hàm xử lý khi nhận được tin nhắn từ Broker
def on_message(client, userdata, msg):
    try:
        # 1. Giải mã JSON
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)
        
        # 2. Kiểm tra tính hợp lệ (Validate)
        if "temperature" not in data or "humidity" not in data:
            print("Dữ liệu không hợp lệ, bỏ qua.")
            return

        # 3. Đóng gói dữ liệu thành Point cho InfluxDB
        point = (
            Point("environment_metrics")
            .tag("device_id", "esp32_simulator")
            .field("temperature", float(data["temperature"]))
            .field("humidity", float(data["humidity"]))
            .field("distance_cm", float(data.get("distance_cm", 0)))
        )
        
        # 4. Ghi vào InfluxDB
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
        print(f"Đã ghi thành công: Nhiệt độ {data['temperature']}°C, Độ ẩm {data['humidity']}%")

    except Exception as e:
        print(f"Lỗi khi xử lý dữ liệu: {e}")

# Khởi tạo MQTT Client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

print("Đang khởi động hệ thống thu thập dữ liệu...")
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Chạy vòng lặp vô hạn để duy trì kết nối
try:
    mqtt_client.loop_forever()
except KeyboardInterrupt:
    print("\nĐã ngắt kết nối an toàn.")
    mqtt_client.disconnect()
    influx_client.close()