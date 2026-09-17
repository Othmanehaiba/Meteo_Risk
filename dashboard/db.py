import os
import pandas as pd
from sqlalchemy import create_engine
import streamlit as st

@st.cache_resource
def get_connection():
    # Variables d'environnement configurées pour PostgreSQL / Docker
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "meteorisk")
    
    url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url)

@st.cache_data(ttl=3600)
def load_data():
    """Charge l'ensemble des données de la table de faits pour Streamlit."""
    engine = get_connection()
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
    return pd.read_sql(query, engine)