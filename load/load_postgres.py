import os
import pandas as pd
from sqlalchemy import create_engine, text

def get_db_engine():
    # Récupération des variables d'environnement (compatibles Docker)
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "meteorisk")
    
    url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url)

def load_gold_to_postgres():
    gold_path = "data/gold/weather_risk_gold.csv"
    if not os.path.exists(gold_path):
        raise FileNotFoundError(f"Le fichier {gold_path} n'existe pas.")

    df = pd.read_csv(gold_path)
    engine = get_db_engine()

    # 1. Exécution du schéma SQL
    schema_path = "load/schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    
    with engine.begin() as connection:
        connection.execute(text(schema_sql))

    # 2. Insertion / Mise à jour dans dim_villes
    villes_df = df[['ville', 'region', 'lat', 'lon']].drop_duplicates()
    with engine.begin() as connection:
        for _, row in villes_df.iterrows():
            sql = text("""
                INSERT INTO dim_villes (nom_ville, region, latitude, longitude)
                VALUES (:ville, :region, :lat, :lon)
                ON CONFLICT (nom_ville) DO UPDATE SET
                    region = EXCLUDED.region,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude;
            """)
            connection.execute(sql, {
                "ville": row['ville'],
                "region": row['region'],
                "lat": row['lat'],
                "lon": row['lon']
            })

    # 3. Stratégie UPSERT pour fact_previsions_risques
    with engine.begin() as connection:
        for _, row in df.iterrows():
            sql = text("""
                INSERT INTO fact_previsions_risques (
                    nom_ville, date_prevision, temp_max, temp_min,
                    precipitation, precipitation_prob, wind_speed, wind_gusts,
                    weather_code, wind_category, precip_category, temp_category,
                    risk_score, risk_level, updated_at
                )
                VALUES (
                    :ville, :date, :temp_max, :temp_min,
                    :precip, :precip_prob, :wind, :wind_gusts,
                    :w_code, :w_cat, :p_cat, :t_cat,
                    :score, :level, NOW()
                )
                ON CONFLICT (nom_ville, date_prevision) DO UPDATE SET
                    temp_max = EXCLUDED.temp_max,
                    temp_min = EXCLUDED.temp_min,
                    precipitation = EXCLUDED.precipitation,
                    precipitation_prob = EXCLUDED.precipitation_prob,
                    wind_speed = EXCLUDED.wind_speed,
                    wind_gusts = EXCLUDED.wind_gusts,
                    weather_code = EXCLUDED.weather_code,
                    wind_category = EXCLUDED.wind_category,
                    precip_category = EXCLUDED.precip_category,
                    temp_category = EXCLUDED.temp_category,
                    risk_score = EXCLUDED.risk_score,
                    risk_level = EXCLUDED.risk_level,
                    updated_at = NOW();
            """)
            connection.execute(sql, {
                "ville": row['ville'], "date": row['date'],
                "temp_max": row['temp_max'], "temp_min": row['temp_min'],
                "precip": row['precipitation'], "precip_prob": row['precipitation_prob'],
                "wind": row['wind_speed'], "wind_gusts": row['wind_gusts'],
                "w_code": row['weather_code'], "w_cat": row['wind_category'],
                "p_cat": row['precip_category'], "t_cat": row['temp_category'],
                "score": row['risk_score'], "level": row['risk_level']
            })

    print("[PostgreSQL] Données Gold chargées avec succès sans doublons !")

if __name__ == "__main__":
    load_gold_to_postgres()