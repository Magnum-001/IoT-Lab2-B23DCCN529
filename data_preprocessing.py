import pandas as pd
import numpy as np
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from sklearn.preprocessing import MinMaxScaler

# ================= 1. CẤU HÌNH INFLUXDB =================
INFLUX_URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUX_TOKEN = "OJ-0mr90axwEmHyEDyGgg07k7fVYpsOCf-PdPkAksMiHYm9yrEH04FzjC1P8Fve2cZ3mfuIR8dxhBdkedStytA=="
INFLUX_ORG = "Magnum"
INFLUX_BUCKET = "sensor" # Sửa lại đúng tên bucket của em

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
query_api = client.query_api()
write_api = client.write_api(write_options=SYNCHRONOUS)

# ================= 2. TRUY VẤN DỮ LIỆU (READ) =================
print("Đang tải dữ liệu thô trong 1 giờ qua...")
query = f'''
    from(bucket: "{INFLUX_BUCKET}")
    |> range(start: -1h)
    |> filter(fn: (r) => r["_measurement"] == "environment_metrics")
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
'''
df = query_api.query_data_frame(query, org=INFLUX_ORG)

# Kiểm tra nếu dataframe rỗng
if isinstance(df, list):
    if len(df) == 0:
        print("Không có dữ liệu trong khoảng thời gian này.")
        exit()
    df = df[0]

# Giữ lại các cột cần thiết và set index là thời gian
df = df[['_time', 'temperature', 'humidity', 'distance_cm']]
df['_time'] = pd.to_datetime(df['_time'])
df.set_index('_time', inplace=True)

# ================= 3. TIỀN XỬ LÝ DỮ LIỆU =================
print("Đang tiến hành tiền xử lý dữ liệu...")

# a. Xử lý giá trị thiếu (Missing values)
df.ffill(inplace=True) # Điền bằng giá trị ngay trước đó

# b. Phát hiện và xử lý Outlier bằng IQR cho nhiệt độ
Q1 = df['temperature'].quantile(0.25)
Q3 = df['temperature'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
# Thay thế giá trị ngoại lai bằng giá trị trung vị
median_temp = df['temperature'].median()
df['temperature'] = np.where((df['temperature'] < lower_bound) | (df['temperature'] > upper_bound), median_temp, df['temperature'])

# c. Resampling theo cửa sổ thời gian 1 phút
df_resampled = df.resample('1min').mean().dropna()

# d. Tạo đặc trưng (Feature Engineering) - Sinh thêm cột delta nhiệt độ
df_resampled['temp_delta'] = df_resampled['temperature'].diff().fillna(0)

# e. Chuẩn hóa dữ liệu (Normalization) theo thang 0-1
scaler = MinMaxScaler()
df_normalized = pd.DataFrame(scaler.fit_transform(df_resampled), columns=df_resampled.columns, index=df_resampled.index)

# ================= 4. GHI DỮ LIỆU ĐÃ XỬ LÝ VÀO DATABASE =================
print("Đang ghi dữ liệu đã làm sạch vào cơ sở dữ liệu...")
for index, row in df_normalized.iterrows():
    point = (
        Point("environment_metrics_clean") # Tên measurement mới cho dữ liệu sạch
        .tag("processing_method", "iqr_minmax")
        .field("temperature_norm", float(row['temperature']))
        .field("humidity_norm", float(row['humidity']))
        .field("temp_delta_norm", float(row['temp_delta']))
    )
    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

print("Hoàn tất tiền xử lý và lưu trữ!")
client.close()