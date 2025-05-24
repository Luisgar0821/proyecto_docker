
# 🔬 Proyecto ETL y Streaming: Predicción de Cáncer de Pulmón

Este proyecto implementa un **pipeline ETL completo** utilizando Airflow, PostgreSQL, y Apache Kafka para procesar y transmitir métricas sobre el cáncer de pulmón a partir de datos de salud. Incluye además dashboards estáticos en Power BI y visualización **en tiempo real** con Streamlit.

---

## 📌 Objetivo

El objetivo principal es procesar datos provenientes de un dataset masivo y una API externa, transformarlos y cargarlos en un **modelo dimensional en PostgreSQL**, y luego transmitir métricas clave en tiempo real a través de **Apache Kafka**, visualizándolas mediante un dashboard interactivo.

Este sistema busca simular un entorno real de monitoreo de salud pública relacionado con el cáncer de pulmón, su prevalencia, hábitos de tabaquismo, y el acceso al sistema de salud.

---

## 🛠️ Tecnologías utilizadas

- **Apache Airflow**: Orquestación de tareas ETL
- **PostgreSQL**: Base de datos relacional para almacenar el modelo dimensional
- **Apache Kafka**: Sistema de mensajería para transmisión en tiempo real
- **Python + Pandas**: Transformaciones de datos y servicios
- **Streamlit**: Dashboard en tiempo real
- **Power BI**: Dashboard exploratorio offline
- **Docker / Docker Compose**: Contenedores y despliegue

---

## 🗂️ Estructura del Proyecto

```
├── airflow/
│   ├── dags/
│   │   ├── etl_load_postgres_dag.py
│   │   ├── temp_api_data.csv
│   │   ├── temp_transformed.csv
│   │   └── temp_merged.csv
├── kafka/
│   ├── producer.py
│   ├── consumer.py
│   └── dashboard/
│       ├── realtime_dashboard.py
│       ├── message_store.py
│       └── Dockerfile.streamlit
├── Docker/
│   ├── docker-compose.yml
│   ├── Dockerfile.airflow
│   └── create_schema.sql
├── Notebooks/
│   └── lung_cancer_EDA.ipynb
├── Dashboard/
│   └── Dashboard modelo dimensional.pdf
├── test/
│   ├── test_api.py
│   └── test_transform_data.py
└── requirements.txt
```

---

## 🔄 Flujo ETL y de Streaming

### 1. **Extracción**
- Datos de un CSV local (`lung_cancer_prediction_dataset.csv`)
- Datos desde la API de la OMS sobre tabaquismo

### 2. **Transformación**
- Limpieza, mapeo booleano, agrupación por país
- Sustitución de nulos con el valor `"any"` cuando representa casos no diagnosticados

### 3. **Carga**
- Se insertan datos en un **modelo dimensional** en PostgreSQL con claves foráneas:
  - Dimensiones: país, salud, fumador, exposición, diagnóstico, tratamiento, estadio
  - Tabla de hechos: hechos_persona

### 4. **Streaming**
- Kafka `producer.py` extrae métricas agregadas desde PostgreSQL
- Kafka `consumer.py` recibe los datos para validación
- Streamlit visualiza las métricas en tiempo real

---

## 📊 Dashboards

- **Power BI**: análisis exploratorio por país, tabaquismo, acceso a salud (ver carpeta `Dashboard/`)
- **Streamlit (tiempo real)**: últimos valores enviados desde Kafka (años fumando, cigarrillos/día, tasa de prevalencia y mortalidad)

---

## ▶️ Cómo ejecutar el proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/usuario/etl-lung-cancer.git
cd etl-lung-cancer/Docker
```

### 2. Levantar los servicios con Docker Compose

```bash
docker-compose up --build
```

Este comando iniciará:
- PostgreSQL con el esquema creado automáticamente
- Airflow Webserver y Scheduler
- Kafka y Zookeeper
- Productor y consumidor Kafka
- Dashboard Streamlit accesible en `http://localhost:8501`
- Airflow accesible en `http://localhost:8080` (usuario: `airflow`, contraseña: `airflow`)
- Kafka UI accesible en `http://localhost:8089`

### 3. Ejecutar el DAG desde Airflow

1. Ir a `http://localhost:8080`
2. Activar y lanzar el DAG llamado `etl_dimensional_model`

---

## ✅ Requisitos del sistema

- Docker Desktop
- Puertos disponibles: 5433, 8080, 8501, 8089
- Espacio disponible: ~2GB

---

## 🧪 Pruebas Unitarias

Se incluyen pruebas con `pytest` en el directorio `test/`, donde se valida:

- Extracción y filtrado desde la API
- Transformación de nombres de país y limpieza de valores

Para correrlas:

```bash
pip install -r requirements.txt
pytest test/
```

---


## 👤 Autor

- **Luis Ángel García (2230177)**
- **Antnio Cardenas jurado (2230433)** 
- **Juliana Toro (2225658)** 

---


