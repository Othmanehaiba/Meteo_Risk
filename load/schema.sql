CREATE TABLE IF NOT EXISTS dim_villes (
    ville_id SERIAL PRIMARY KEY,
    nom_ville VARCHAR(100) UNIQUE NOT NULL,
    region VARCHAR(100),
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_previsions_risques (
    prevision_id SERIAL PRIMARY KEY,
    nom_ville VARCHAR(100) NOT NULL,
    date_prevision DATE NOT NULL,
    temp_max FLOAT,
    temp_min FLOAT,
    precipitation FLOAT,
    precipitation_prob FLOAT,
    wind_speed FLOAT,
    wind_gusts FLOAT,
    weather_code INT,
    wind_category VARCHAR(20),
    precip_category VARCHAR(20),
    temp_category VARCHAR(20),
    risk_score FLOAT NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contrainte d'unicité pour éviter les doublons lors des réexécutions
    CONSTRAINT unique_ville_date UNIQUE (nom_ville, date_prevision)
);