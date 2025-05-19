from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import psycopg2
import os
import requests
import pycountry

# Rutas de archivos temporales
CSV_PATH = "/opt/airflow/dags/DATASET/lung_cancer_prediction_dataset.csv"
TEMP_PATH = '/opt/airflow/dags/temp_transformed.csv'
API_PATH = "/opt/airflow/dags/temp_api_data.csv"
MERGED_PATH = '/opt/airflow/dags/temp_merged.csv'

# Task 1: Extraer datos CSV
def extract_csv():
    df = pd.read_csv(CSV_PATH)
    df.to_csv(TEMP_PATH, index=False)

# Task 2: Extraer datos API
def extract_api():
    url = "https://ghoapi.azureedge.net/api/WHOSIS_000001"
    response = requests.get(url)
    data = response.json()['value']
    rows = []
    for i in data:
        if all(k in i for k in ['SpatialDim', 'TimeDim', 'Value']) and i['TimeDim'] >= 2018:
            rows.append({
                "country_code": i.get('SpatialDim'),
                "smoking_prevalence": i.get('Value')
            })
    df_api = pd.DataFrame(rows)
    df_api.to_csv(API_PATH, index=False)

# Task 3: Transformar CSV
def transform_data():
    df = pd.read_csv(TEMP_PATH)

    selected_columns = [
        "Age", "Country", "Lung_Cancer_Prevalence_Rate", "Smoker", "Years_of_Smoking",
        "Cigarettes_per_Day", "Passive_Smoker", "Lung_Cancer_Diagnosis", "Healthcare_Access",
        "Early_Detection", "Survival_Years", "Developed_or_Developing", "Mortality_Rate",
        "Annual_Lung_Cancer_Deaths", "Air_Pollution_Exposure", "Occupational_Exposure",
        "Indoor_Pollution", "Family_History", "Treatment_Type", "Cancer_Stage"
    ]
    df = df[selected_columns]

    # Mapear valores tipo 'Yes'/'No' a booleanos
    bool_cols = ['Smoker', 'Passive_Smoker', 'Family_History', 'Occupational_Exposure',
                 'Indoor_Pollution', 'Early_Detection']
    for col in bool_cols:
        df[col] = df[col].map({'Yes': True, 'No': False})

    # Reemplazar nulos con 'Ninguno' en columnas categóricas
    df['Treatment_Type'] = df['Treatment_Type'].fillna("Ninguno")
    df['Cancer_Stage'] = df['Cancer_Stage'].fillna("Ninguno")

    df.to_csv(TEMP_PATH, index=False)

# Task 4: Transformar API
def transform_api():
    df = pd.read_csv(API_PATH)

    # Traducir códigos de país a nombres
    def get_country_name(code):
        try:
            return pycountry.countries.get(alpha_3=code).name
        except:
            return None
    df["country"] = df["country_code"].apply(get_country_name)

    # Extraer solo el valor promedio de smoking_prevalence (antes del espacio)
    def limpiar_smoking_prevalence(valor):
        try:
            return float(str(valor).split(" ")[0])
        except:
            return None
    df["smoking_prevalence"] = df["smoking_prevalence"].apply(limpiar_smoking_prevalence)

    # Agrupar por país y sacar un único valor promedio
    df = df.groupby("country", as_index=False)["smoking_prevalence"].mean()

    df.to_csv(API_PATH, index=False)

# Task 5: Hacer merge
def merge_data():
    df_csv = pd.read_csv(TEMP_PATH)
    df_api = pd.read_csv(API_PATH)
    df_merged = pd.merge(df_csv, df_api, left_on='Country', right_on='country', how='left')
    df_merged.dropna(subset=['smoking_prevalence'], inplace=True)
    df_merged.drop(columns=[col for col in ['country_code', 'country'] if col in df_merged.columns], inplace=True)
    df_merged.to_csv(MERGED_PATH, index=False)

# Task 6: Poblar modelo dimensional

def populate_dimensional_model():
    df = pd.read_csv(MERGED_PATH)
    conn = psycopg2.connect(
        dbname='lung_cancer',
        user='postgres',
        password='123456',
        host='db',
        port='5432'
    )
    cur = conn.cursor()

    def get_or_create_country(name, developed_status, smoking_prevalence):
        cur.execute("SELECT id FROM dim_country WHERE country_name = %s", (name,))
        result = cur.fetchone()
        if result:
            cur.execute("""
                UPDATE dim_country SET developed_status = %s, smoking_prevalence = %s WHERE id = %s
            """, (developed_status, smoking_prevalence, result[0]))
            return result[0]
        cur.execute("""
            INSERT INTO dim_country (country_name, developed_status, smoking_prevalence)
            VALUES (%s, %s, %s) RETURNING id
        """, (name, developed_status, smoking_prevalence))
        return cur.fetchone()[0]

    def get_or_create_salud(healthcare_access, early_detection):
        cur.execute("""
            SELECT id FROM dim_salud WHERE healthcare_access = %s AND early_detection = %s
        """, (healthcare_access, early_detection))
        result = cur.fetchone()
        if result:
            return result[0]
        cur.execute("""
            INSERT INTO dim_salud (healthcare_access, early_detection)
            VALUES (%s, %s) RETURNING id
        """, (healthcare_access, early_detection))
        return cur.fetchone()[0]

    def get_or_create_id(table, column, value):
        cur.execute(f"SELECT id FROM {table} WHERE {column} = %s", (value,))
        result = cur.fetchone()
        if result:
            return result[0]
        cur.execute(f"INSERT INTO {table} ({column}) VALUES (%s) RETURNING id", (value,))
        return cur.fetchone()[0]

    def get_or_create_exposicion(air_pollution, occupational, indoor, passive, family_history):
        cur.execute("""
            SELECT id FROM dim_exposicion
            WHERE air_pollution_exposure = %s AND occupational_exposure = %s
            AND indoor_pollution = %s AND passive_smoker = %s AND family_history = %s
        """, (air_pollution, occupational, indoor, passive, family_history))
        result = cur.fetchone()
        if result:
            return result[0]
        cur.execute("""
            INSERT INTO dim_exposicion (
                air_pollution_exposure, occupational_exposure, indoor_pollution,
                passive_smoker, family_history
            ) VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (air_pollution, occupational, indoor, passive, family_history))
        return cur.fetchone()[0]

    def get_or_create_fumador(smoker):
        cur.execute("""
            SELECT id FROM dim_fumador WHERE smoker = %s
        """, (smoker,))
        result = cur.fetchone()
        if result:
            return result[0]
        cur.execute("""
            INSERT INTO dim_fumador (smoker) VALUES (%s) RETURNING id
        """, (smoker,))
        return cur.fetchone()[0]

    for _, row in df.iterrows():
        country_id = get_or_create_country(
            row['Country'], row['Developed_or_Developing'], row['smoking_prevalence']
        )
        salud_id = get_or_create_salud(row['Healthcare_Access'], row['Early_Detection'])
        tratamiento_id = get_or_create_id('dim_tratamiento', 'treatment_type', row['Treatment_Type'])
        cancer_stage_id = get_or_create_id('dim_cancer_stage', 'cancer_stage', row['Cancer_Stage'])
        diagnostico_id = get_or_create_id('dim_diagnostico', 'diagnostico', row['Lung_Cancer_Diagnosis'])
        exposicion_id = get_or_create_exposicion(
            row['Air_Pollution_Exposure'], row['Occupational_Exposure'],
            row['Indoor_Pollution'], row['Passive_Smoker'], row['Family_History']
        )
        fumador_id = get_or_create_fumador(row['Smoker'])

        cur.execute("""
            INSERT INTO hechos_persona (
                age, years_of_smoking, cigarettes_per_day, survival_years,
                annual_lung_cancer_deaths, lung_cancer_prevalence_rate, mortality_rate,
                country_id, salud_id, tratamiento_id, cancer_stage_id,
                diagnostico_id, fumador_id, exposicion_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row['Age'], row['Years_of_Smoking'], row['Cigarettes_per_Day'], row['Survival_Years'],
            row['Annual_Lung_Cancer_Deaths'], row['Lung_Cancer_Prevalence_Rate'],
            row['Mortality_Rate'], country_id, salud_id, tratamiento_id,
            cancer_stage_id, diagnostico_id, fumador_id, exposicion_id
        ))

    conn.commit()
    cur.close()
    conn.close()

# DAG Definition
with DAG(
    dag_id='etl_dimensional_model',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    description="ETL con modelo dimensional para cáncer de pulmón"
) as dag:

    task_extract_csv = PythonOperator(
        task_id='extract_csv',
        python_callable=extract_csv
    )

    task_extract_api = PythonOperator(
        task_id='extract_api',
        python_callable=extract_api
    )

    task_transform_csv = PythonOperator(
        task_id='transform_csv',
        python_callable=transform_data
    )

    task_transform_api = PythonOperator(
        task_id='transform_api',
        python_callable=transform_api
    )

    task_merge = PythonOperator(
        task_id='merge_data',
        python_callable=merge_data
    )

    task_load_dimensional_model = PythonOperator(
        task_id='populate_dimensional_model',
        python_callable=populate_dimensional_model
    )

    # Dependencias 
    task_extract_csv >> task_transform_csv
    task_extract_api >> task_transform_api
    [task_transform_csv, task_transform_api] >> task_merge
    task_merge >> task_load_dimensional_model
