# consumer.py
from kafka import KafkaConsumer
import json
import time

time.sleep(15)

consumer = KafkaConsumer(
    'lung_cancer_metrics',
    bootstrap_servers='kafka:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='metrics-consumer-group'
)

print("✅ Esperando métricas desde el tópico 'lung_cancer_metrics'...")

for message in consumer:
    data = message.value
    print("\n📊 Métrica recibida:")
    print(f"🌍 País: {data['country']} ({data['developed_status']})")
    print(f"Promedio de años fumando: {data['avg_years_smoking']}")
    print(f"Promedio de cigarrillos por día: {data['avg_cigarettes_per_day']}")
    print(f"Tasa promedio de prevalencia: {data['prevalence_rate']}")
    print(f"Tasa promedio de mortalidad: {data['mortality_rate']}")
