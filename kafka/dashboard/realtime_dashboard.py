import streamlit as st
from kafka import KafkaConsumer
import json
import threading
from datetime import datetime
import time

# ✅ Singleton para persistencia en memoria
class MessageStore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.data = {}
        return cls._instance

    def update(self, country, msg):
        self.data[country] = msg

    def get_data(self):
        return self.data.copy()

store = MessageStore()

st.set_page_config(page_title="Lung Cancer Real-Time Dashboard", layout="wide")
st.title("📊 Lung Cancer Metrics Dashboard (Real Time)")
st.subheader("📌 Últimas métricas recibidas por país:")

# Función que escucha Kafka
def listen_kafka():
    try:
        print("🛰️ Conectando a Kafka...")
        consumer = KafkaConsumer(
            'lung_cancer_metrics',
            bootstrap_servers='kafka:9092',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            group_id='streamlit-dashboard-group'
        )
        print("✅ Conectado a Kafka.")

        for message in consumer:
            msg = message.value
            msg['timestamp'] = datetime.now().strftime("%H:%M:%S")
            store.update(msg['country'], msg)
            print("📨 Mensaje recibido:", msg)

    except Exception as e:
        print("❌ Error al conectar a Kafka:", e)

# Lanzar hilo solo una vez
if 'thread_started' not in st.session_state:
    st.session_state.thread_started = True
    thread = threading.Thread(target=listen_kafka, daemon=True)
    thread.start()

# Obtener datos desde el almacén persistente
data = store.get_data()

# Mostrar en interfaz
if data:
    for country, record in data.items():
        st.markdown(f"### 🌍 {country} ({record['developed_status']})")
        col1, col2, col3 = st.columns(3)
        col1.metric("Años fumando (prom)", record['avg_years_smoking'])
        col2.metric("Cigarrillos/día (prom)", record['avg_cigarettes_per_day'])
        col3.metric("Tasa de prevalencia", record['prevalence_rate'])
        st.metric("Tasa de mortalidad", record['mortality_rate'])
        st.caption(f"🕒 Última actualización: {record['timestamp']}")
else:
    st.warning("⏳ Aún no se han recibido métricas desde Kafka...")

# Mostrar hora de actualización
st.caption(f"📅 Última recarga del dashboard: {datetime.now().strftime('%H:%M:%S')}")

# Auto recarga
time.sleep(10)
st.rerun()
