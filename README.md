# Bài thực hành số 2: Thu thập, lưu trữ và tiền xử lý dữ liệu IoT

**Thông tin sinh viên:**
- Họ và tên: Lê Tiến Mạnh
- Mã SV: B23DCCN529
- Học viện Công nghệ Bưu chính Viễn thông (PTIT)

## 1. Giới thiệu
Dự án mô phỏng quá trình thu thập dữ liệu nhiệt độ, độ ẩm từ vi điều khiển ESP32 (Wokwi), truyền qua giao thức MQTT (HiveMQ) và lưu trữ vào cơ sở dữ liệu chuỗi thời gian InfluxDB. Dữ liệu sau đó được tiền xử lý (xóa nhiễu, chuẩn hóa) bằng Pandas và trực quan hóa lên Dashboard bằng Streamlit.

## 2. Cấu trúc mã nguồn
- `sketch.ino`: Firmware C++ chạy trên ESP32 giả lập (Đọc cảm biến DHT22, gửi MQTT).
- `mqtt_to_influxdb.py`: Kịch bản Python đóng vai trò MQTT Client, nhận dữ liệu và ghi vào InfluxDB.
- `data_preprocessing.py`: Kịch bản Python tiền xử lý (kéo dữ liệu từ InfluxDB, làm sạch, chuẩn hóa và lưu lại).
- `iot_dashboard.py`: Giao diện web hiển thị biểu đồ so sánh dữ liệu thô và dữ liệu sạch.

## 3. Hướng dẫn chạy hệ thống
**Bước 1: Chạy mô phỏng thiết bị**
Copy code `sketch.ino` chạy trên nền tảng Wokwi với board ESP32 và cảm biến DHT22.

**Bước 2: Cài đặt thư viện Python**
Mở Terminal và chạy lệnh:
`pip install paho-mqtt influxdb-client pandas scikit-learn streamlit plotly`

**Bước 3: Chạy luồng thu thập dữ liệu**
Thực thi lệnh sau và giữ cho Terminal chạy ngầm:
`python mqtt_to_influxdb.py`

**Bước 4: Tiền xử lý dữ liệu**
Sau khi có dữ liệu thô, mở một Terminal mới và chạy:
`python data_preprocessing.py`

**Bước 5: Khởi chạy Dashboard giám sát**
Thực thi lệnh sau để mở giao diện web trên trình duyệt:
`streamlit run iot_dashboard.py`
