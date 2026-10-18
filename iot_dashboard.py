import streamlit as st
import pandas as pd
from influxdb_client import InfluxDBClient
import plotly.express as px

# ================= CẤU HÌNH INFLUXDB =================
INFLUX_URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUX_TOKEN = "OJ-0mr90axwEmHyEDyGgg07k7fVYpsOCf-PdPkAksMiHYm9yrEH04FzjC1P8Fve2cZ3mfuIR8dxhBdkedStytA=="
INFLUX_ORG = "Magnum"
INFLUX_BUCKET = "sensor"

# ================= GIAO DIỆN STREAMLIT =================
st.set_page_config(page_title="IoT Monitoring", layout="wide")

st.title("📊 Hệ thống Giám sát Dữ liệu IoT Thời gian thực")
st.markdown("**Sinh viên thực hiện:** Lê Tiến Mạnh | **Mã SV:** B23DCCN529 | **Học viện:** PTIT")
st.markdown("---")

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
query_api = client.query_api()

# Truy vấn dữ liệu từ database
@st.cache_data(ttl=5) # Tự động làm mới mỗi 5 giây
def load_data(measurement_name):
    query = f'''
        from(bucket: "{INFLUX_BUCKET}")
        |> range(start: -30m)
        |> filter(fn: (r) => r["_measurement"] == "{measurement_name}")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    df = query_api.query_data_frame(query, org=INFLUX_ORG)
    if isinstance(df, list):
        if len(df) == 0: return pd.DataFrame()
        df = df[0]
    return df

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Dữ liệu Thô (Từ Cảm biến)")
    df_raw = load_data("environment_metrics")
    if not df_raw.empty:
        fig_raw = px.line(df_raw, x="_time", y=["temperature", "humidity"], 
                          labels={"value": "Giá trị", "_time": "Thời gian"})
        st.plotly_chart(fig_raw, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu thô.")

with col2:
    st.subheader("✨ Dữ liệu Đã Tiền xử lý (Làm sạch)")
    df_clean = load_data("environment_metrics_clean")
    if not df_clean.empty:
        fig_clean = px.line(df_clean, x="_time", y=["temperature_norm", "humidity_norm"], 
                            labels={"value": "Giá trị chuẩn hóa (0-1)", "_time": "Thời gian"})
        st.plotly_chart(fig_clean, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu tiền xử lý.")
        
st.button("🔄 Cập nhật thủ công")