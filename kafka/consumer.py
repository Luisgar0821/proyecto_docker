# consumer.py

from kafka import KafkaConsumer
import json
import time

# Espera para asegurar que Kafka ya esté disponible
time.sleep(15)

# Configurar consumidor Kafka
consumer = KafkaConsumer(
    'lung_cancer_metrics',
    bootstrap_servers='kafka:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest',  # ✅ Solo leer nuevos mensajes
    enable_auto_commit=True,
    group_id='metrics-consumer-group'
)

print("✅ Esperando métricas desde el tópico 'lung_cancer_metrics'...", flush=True)

# Bucle principal
for message in consumer:
    data = message.value
    print("\n📊 Métrica recibida:", flush=True)
    print(f"🌍 País: {data['country']} ({data['developed_status']})", flush=True)
    print(f"Promedio de años fumando: {data['avg_years_smoking']}", flush=True)
    print(f"Promedio de cigarrillos por día: {data['avg_cigarettes_per_day']}", flush=True)
    print(f"Tasa promedio de prevalencia: {data['prevalence_rate']}", flush=True)
    print(f"Tasa promedio de mortalidad: {data['mortality_rate']}", flush=True)
