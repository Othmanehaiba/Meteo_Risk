import os
import pandas as pd
import psycopg2

def load_data():
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "meteorisk")
    
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=db,
        user=user,
        password=password
    )
    
    query = """
        SELECT 
            f.nom_ville,
            f.date_prevision,
            f.temp_max,
            f.temp_min,
            f.precipitation,
            f.precipitation_prob,
            f.wind_speed,
            f.wind_gusts,
            f.wind_category,
            f.precip_category,
            f.temp_category,
            f.risk_score,
            f.risk_level,
            v.region,
            v.latitude,
            v.longitude
        FROM fact_previsions_risques f
        LEFT JOIN dim_villes v ON f.nom_ville = v.nom_ville
        ORDER BY f.date_prevision ASC;
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df