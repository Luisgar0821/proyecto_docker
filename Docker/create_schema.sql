-- País 
CREATE TABLE dim_country (
    id SERIAL PRIMARY KEY,
    country_name VARCHAR(100) UNIQUE,
    developed_status VARCHAR(50),
    smoking_prevalence FLOAT
);

-- Salud
CREATE TABLE dim_salud (
    id SERIAL PRIMARY KEY,
    healthcare_access VARCHAR(50),
    early_detection BOOLEAN
);

-- Tratamiento
CREATE TABLE dim_tratamiento (
    id SERIAL PRIMARY KEY,
    treatment_type VARCHAR(50) UNIQUE
);

-- Estadio del cáncer
CREATE TABLE dim_cancer_stage (
    id SERIAL PRIMARY KEY,
    cancer_stage VARCHAR(50) UNIQUE
);

-- Diagnóstico
CREATE TABLE dim_diagnostico (
    id SERIAL PRIMARY KEY,
    diagnostico VARCHAR(50) UNIQUE
);

-- Fumador
CREATE TABLE dim_fumador (
    id SERIAL PRIMARY KEY,
    smoker BOOLEAN
);

-- Exposición ambiental
CREATE TABLE dim_exposicion (
    id SERIAL PRIMARY KEY,
    air_pollution_exposure VARCHAR(50),
    occupational_exposure BOOLEAN,
    indoor_pollution BOOLEAN,
    passive_smoker BOOLEAN,
    family_history BOOLEAN
);

-- TABLA DE HECHOS
CREATE TABLE hechos_persona (
    id SERIAL PRIMARY KEY,
    age INT,
    years_of_smoking INT,
    cigarettes_per_day INT,
    survival_years INT,
    annual_lung_cancer_deaths INT,
    lung_cancer_prevalence_rate FLOAT,
    mortality_rate FLOAT,

    -- Claves foráneas
    country_id INT REFERENCES dim_country(id),
    salud_id INT REFERENCES dim_salud(id),
    tratamiento_id INT REFERENCES dim_tratamiento(id),
    cancer_stage_id INT REFERENCES dim_cancer_stage(id),
    diagnostico_id INT REFERENCES dim_diagnostico(id),
    fumador_id INT REFERENCES dim_fumador(id),
    exposicion_id INT REFERENCES dim_exposicion(id)
);