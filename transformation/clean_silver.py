import os
import json
import pandas as pd

def run_silver_pipeline():
    
    bronze_dir = "data/bronze"
    silver_dir = "data/silver"
    os.makedirs(silver_dir, exist_ok=True) #creates the silver directory if it doesn't exist

    # 2. Chargement du fichier CSV des villes
    villes_path = os.path.join(bronze_dir, "ma.csv")
    df_villes = pd.read_csv(villes_path)
    
    # Nettoyage et sélection des colonnes utiles des villes
    df_villes = df_villes[['city', 'lat', 'lon', 'admin_name']].drop_duplicates()
    df_villes.rename(columns={'city': 'ville', 'admin_name': 'region'}, inplace=True)
    # 3. Traitement des prévisions météo brutes (JSON)
    weather_records = []
    
    for filename in os.listdir(bronze_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(bronze_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Extraire les métadonnées et la section daily
                ville_name = data.get("ville")
                daily = data.get("daily", {})
                
                # Transformer le dictionnaire daily en DataFrame plat (1 ligne par jour)
                if daily and "time" in daily:
                    df_daily = pd.DataFrame(daily)
                    df_daily["ville"] = ville_name
                    weather_records.append(df_daily)
                    # 4. Fusion des prévisions et nettoyage global
    if not weather_records:
        raise ValueError("Aucune donnée météo trouvée dans Bronze.")
        
    df_weather = pd.concat(weather_records, ignore_index=True)
    
    # Standardisation des noms de colonnes météo
    df_weather.rename(columns={
        'time': 'date',
        'temperature_2m_max': 'temp_max',
        'temperature_2m_min': 'temp_min',
        'precipitation_sum': 'precipitation',
        'precipitation_probability_max': 'precipitation_prob',
        'wind_speed_10m_max': 'wind_speed',
        'wind_gusts_10m_max': 'wind_gusts',
        'weather_code': 'weather_code'
    }, inplace=True)

    # 5. Typer, valider la qualité et supprimer les doublons
    df_weather['date'] = pd.to_datetime(df_weather['date']).dt.date
    
    cols_num = ['temp_max', 'temp_min', 'precipitation', 'precipitation_prob', 'wind_speed', 'wind_gusts']
    for col in cols_num:
        if col in df_weather.columns:
            df_weather[col] = pd.to_numeric(df_weather[col], errors='coerce')
            
    # Traitement des doublons sur le couple (ville, date)
    df_weather.drop_duplicates(subset=['ville', 'date'], keep='last', inplace=True)

    # 6. Jointure Silver entre Villes et Météo
    df_silver = pd.merge(df_weather, df_villes, on='ville', how='inner')
    
    # 7. Sauvegarde dans le dossier Silver
    output_path = os.path.join(silver_dir, "weather_cleaned.csv")
    df_silver.to_csv(output_path, index=False)
    print(f"[Silver] Données nettoyées enregistrées dans {output_path}")

if __name__ == "__main__":
    run_silver_pipeline()