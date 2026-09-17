import os
import json
import time
import requests
import pandas as pd

# URL de l'API Open-Meteo pour les prévisions quotidiennes
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

def fetch_weather_for_city(lat, lon):
    """
    Appelle l'API Open-Meteo pour une latitude et longitude données.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
            "weather_code"
        ],
        "timezone": "auto"
    }
    
    try:
        response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[Erreur API] Échec pour la position ({lat}, {lon}) : {e}")
        return None

def run_extraction():
    bronze_dir = "data/bronze"
    villes_csv = os.path.join(bronze_dir, "ma.csv")
    
    if not os.path.exists(villes_csv):
        raise FileNotFoundError(f"Le fichier des villes {villes_csv} est introuvable.")

    # 1. Lire la liste des villes marocaines depuis Bronze
    df_villes = pd.read_csv(villes_csv)
    
    # Prendre les colonnes nécessaires (nom, lat, lon) et supprimer les doublons    
    df_villes = df_villes[['city', 'lat', 'lon']].drop_duplicates()
    
    print(f"[Extraction] Début de la récupération météo pour {len(df_villes)} villes...")

    # 2. Boucler sur chaque ville et interroger Open-Meteo
    for _, row in df_villes.iterrows():
        ville_name = row['city']
        lat = row['lat']
        lon = row['lon']
        
        data = fetch_weather_for_city(lat, lon)
        
        if data:
            # Ajouter le nom de la ville dans les données brutes
            data["ville"] = ville_name
            
            # Sauvegarder chaque prévision au format JSON dans data/bronze/
            filename = f"{ville_name.lower().replace(' ', '_')}.json"
            filepath = os.path.join(bronze_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
            print(f"[Succès] Prévisions enregistrées : {filepath}")
            
        # Pause de précaution pour l'API
        time.sleep(0.2)

    print("[Extraction] Terminée avec succès !")

if __name__ == "__main__":
    run_extraction()