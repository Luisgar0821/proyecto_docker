import pandas as pd
import pytest
import pycountry

# Función 1: transformación desde la API cruda
def extract_api_data(api_response):
    rows = []
    for i in api_response:
        if all(k in i for k in ['SpatialDim', 'TimeDim', 'Value']) and i['TimeDim'] >= 2018:
            rows.append({
                "country_code": i.get('SpatialDim'),
                "smoking_prevalence": i.get('Value')
            })
    return pd.DataFrame(rows)

# Función 2: transformación y limpieza del DataFrame
def transform_api_data(df):
    def get_country_name(code):
        try:
            return pycountry.countries.get(alpha_3=code).name
        except:
            return None

    df["country"] = df["country_code"].apply(get_country_name)

    def limpiar_smoking_prevalence(valor):
        try:
            return float(str(valor).split(" ")[0])
        except:
            return None

    df["smoking_prevalence"] = df["smoking_prevalence"].apply(limpiar_smoking_prevalence)

    return df.groupby("country", as_index=False)["smoking_prevalence"].mean()

# === TEST: Extract ===
def test_extract_api_data():
    fake_api_response = [
        {"SpatialDim": "COL", "TimeDim": 2019, "Value": "12.5"},
        {"SpatialDim": "ARG", "TimeDim": 2020, "Value": "15.1"},
        {"SpatialDim": "MEX", "TimeDim": 2017, "Value": "10.0"},  # debería ser ignorado
    ]

    df = extract_api_data(fake_api_response)

    assert df.shape[0] == 2  # Solo deben quedar 2 filas con TimeDim >= 2018
    assert "country_code" in df.columns
    assert "smoking_prevalence" in df.columns
    assert df["country_code"].tolist() == ["COL", "ARG"]
    assert df["smoking_prevalence"].tolist() == ["12.5", "15.1"]

# === TEST: Transform ===
def test_transform_api_data():
    df_raw = pd.DataFrame({
        "country_code": ["COL", "ARG", "COL"],
        "smoking_prevalence": ["12.5", "15.1", "13.0"]
    })

    df_result = transform_api_data(df_raw)

    # Validamos nombres de países traducidos
    assert set(df_result["country"].dropna()) == {"Colombia", "Argentina"}

    # Validamos que haya un promedio para cada país
    col_value = df_result[df_result["country"] == "Colombia"]["smoking_prevalence"].values[0]
    assert round(col_value, 2) == 12.75

    arg_value = df_result[df_result["country"] == "Argentina"]["smoking_prevalence"].values[0]
    assert round(arg_value, 2) == 15.1
