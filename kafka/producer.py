# producer.py

from kafka import KafkaProducer
import psycopg2
import json
import time
import random

# Esperar a que Kafka y la base estén listos
time.sleep(30)

# Inicializar productor Kafka
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Conexión a PostgreSQL
conn = psycopg2.connect(
    dbname='lung_cancer',
    user='postgres',
    password='123456',
    host='db',
    port='5432'
)
cur = conn.cursor()

# Bucle principal
while True:
    cur.execute("""
        SELECT 
            c.country_name,
            c.developed_status,
            ROUND(AVG(h.years_of_smoking)::numeric, 2) AS avg_years_smoking,
            ROUND(AVG(h.cigarettes_per_day)::numeric, 2) AS avg_cigarettes_per_day,
            ROUND(AVG(h.lung_cancer_prevalence_rate)::numeric, 4) AS prevalence_rate,
            ROUND(AVG(h.mortality_rate)::numeric, 4) AS mortality_rate
        FROM hechos_persona h
        JOIN dim_country c ON h.country_id = c.id
        GROUP BY c.country_name, c.developed_status;
    """)

    rows = cur.fetchall()

    if rows:
        row = random.choice(rows)

        message = {
            'country': row[0],
            'developed_status': row[1],
            'avg_years_smoking': float(row[2]),
            'avg_cigarettes_per_day': float(row[3]),
            'prevalence_rate': float(row[4]),
            'mortality_rate': float(row[5])
        }

        producer.send('lung_cancer_metrics', message)
        print(f"✅ Enviado aleatorio: {message}")

    time.sleep(30)
