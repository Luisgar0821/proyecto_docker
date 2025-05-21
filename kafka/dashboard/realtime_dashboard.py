import streamlit as st
from kafka import KafkaConsumer
import json
import threading
from datetime import datetime
import time
from message_store import shared_data  # importa la misma lista viva

st.set_page_config(page_title="Lung Cancer Real-Time Dashboard", layout="wide")
st.title("📊 Lung Cancer Metrics Dashboard (Último mensaje)")
st.subheader("📌 Última métrica recibida:")

# Hilo que escucha Kafka y guarda siempre el último mensaje
def listen_kafka():
    try:
        print("🛰️ Conectando a Kafka...", flush=True)
        consumer = KafkaConsumer(
            'lung_cancer_metrics',
            bootstrap_servers='kafka:9092',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            group_id='streamlit-dashboard-group'
        )
        print("✅ Conectado a Kafka.", flush=True)

        for message in consumer:
            msg = message.value
            msg['timestamp'] = datetime.now().strftime("%H:%M:%S")

            shared_data.clear()
            shared_data.append(msg)

            print("📨 Último mensaje recibido:", msg, flush=True)

    except Exception as e:
        print("❌ Error al conectar a Kafka:", e, flush=True)

# Lanzar el hilo una sola vez
if "kafka_thread" not in st.session_state:
    thread = threading.Thread(target=listen_kafka, daemon=True)
    thread.start()
    st.session_state.kafka_thread = thread

# Mostrar el último mensaje
if shared_data:
    last = shared_data[-1]
    country = last.get('country', 'País desconocido')
    st.markdown(f"### 🌍 {country} ({last.get('developed_status', '-')})")

    col1, col2, col3 = st.columns(3)
    col1.metric("Años fumando (prom)", round(last.get('avg_years_smoking', 0), 2))
    col2.metric("Cigarrillos/día (prom)", round(last.get('avg_cigarettes_per_day', 0), 2))
    col3.metric("Tasa de prevalencia", round(last.get('prevalence_rate', 0), 2))
    st.metric("Tasa de mortalidad", round(last.get('mortality_rate', 0), 2))
    st.caption(f"Última actualización: {last.get('timestamp', '-')}")
else:
    st.warning("Esperando el primer mensaje...")

st.caption(f"Última recarga: {datetime.now().strftime('%H:%M:%S')}")

# Recarga automática
time.sleep(2)
st.rerun()
