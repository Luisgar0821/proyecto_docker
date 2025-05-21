import pandas as pd
import pytest

# === Función a testear ===
def transform_data(df):
    selected_columns = [
        "Age", "Country", "Lung_Cancer_Prevalence_Rate", "Smoker", "Years_of_Smoking",
        "Cigarettes_per_Day", "Passive_Smoker", "Lung_Cancer_Diagnosis", "Healthcare_Access",
        "Early_Detection", "Survival_Years", "Developed_or_Developing", "Mortality_Rate",
        "Annual_Lung_Cancer_Deaths", "Air_Pollution_Exposure", "Occupational_Exposure",
        "Indoor_Pollution", "Family_History", "Treatment_Type", "Cancer_Stage"
    ]
    df = df[selected_columns]

    bool_cols = ['Smoker', 'Passive_Smoker', 'Family_History', 'Occupational_Exposure',
                 'Indoor_Pollution', 'Early_Detection']
    for col in bool_cols:
        df[col] = df[col].map({'Yes': True, 'No': False})

    df['Treatment_Type'] = df['Treatment_Type'].fillna("Ninguno")
    df['Cancer_Stage'] = df['Cancer_Stage'].fillna("Ninguno")

    return df

# === Parámetros para prueba parametrizada ===
@pytest.mark.parametrize("smoker_input, expected_bool", [
    ("Yes", True),
    ("No", False),
])
def test_smoker_transformation(smoker_input, expected_bool):
    data = {
        "Age": [70],
        "Country": ["Testland"],
        "Lung_Cancer_Prevalence_Rate": [1.5],
        "Smoker": [smoker_input],
        "Years_of_Smoking": [20],
        "Cigarettes_per_Day": [15],
        "Passive_Smoker": ["No"],
        "Lung_Cancer_Diagnosis": ["No"],
        "Healthcare_Access": ["Good"],
        "Early_Detection": ["No"],
        "Survival_Years": [3],
        "Developed_or_Developing": ["Developed"],
        "Mortality_Rate": [0.5],
        "Annual_Lung_Cancer_Deaths": [1000],
        "Air_Pollution_Exposure": ["Medium"],
        "Occupational_Exposure": ["Yes"],
        "Indoor_Pollution": ["No"],
        "Family_History": ["No"],
        "Treatment_Type": [None],
        "Cancer_Stage": [None],
    }

    df_input = pd.DataFrame(data)
    df_result = transform_data(df_input)

    # Verifica el mapeo booleano del campo Smoker
    assert df_result.loc[0, "Smoker"] == expected_bool
    # Verifica que campos nulos hayan sido reemplazados
    assert df_result.loc[0, "Treatment_Type"] == "Ninguno"
    assert df_result.loc[0, "Cancer_Stage"] == "Ninguno"
