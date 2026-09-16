import os
import pandas as pd
import numpy as np

def calculate_risk_score(row):
    # 1. Sous-score Vent (Poids: 40%) - Danger de retournement des camions
    wind = row.get('wind_speed', 0)
    if wind > 70:
        score_wind = 100
    elif wind > 45:
        score_wind = 65
    elif wind > 25:
        score_wind = 30
    else:
        score_wind = 0

    # 2. Sous-score Précipitations (Poids: 40%) - Danger d'inondations/glissades
    precip = row.get('precipitation', 0)
    if precip > 30:
        score_precip = 100
    elif precip > 15:
        score_precip = 70
    elif precip > 5:
        score_precip = 35
    else:
        score_precip = 0

    # 3. Sous-score Température Extrême (Poids: 20%) - Surchauffe / Risque marchandise
    temp = row.get('temp_max', 25)
    if temp > 42 or temp < 0:
        score_temp = 100
    elif temp > 36 or temp < 5:
        score_temp = 50
    else:
        score_temp = 0

    # Formule du Score Global Pondéré (0 à 100)
    total_score = (score_wind * 0.40) + (score_precip * 0.40) + (score_temp * 0.20)
    return round(total_score, 2)

def categorize_weather(row):
    # Catégorisation du Vent
    w = row.get('wind_speed', 0)
    wind_cat = 'Fort' if w > 50 else ('Modéré' if w > 25 else 'Faible')

    # Catégorisation de la Pluie
    p = row.get('precipitation', 0)
    precip_cat = 'Forte' if p > 20 else ('Modérée' if p > 5 else 'Nulle/Faible')

    # Catégorisation de la Température
    t = row.get('temp_max', 20)
    temp_cat = 'Extrême' if t > 40 else ('Élevée' if t > 32 else 'Normale')

    return pd.Series([wind_cat, precip_cat, temp_cat])

def run_gold_pipeline():
    silver_path = "data/silver/weather_cleaned.csv"
    gold_dir = "data/gold"
    os.makedirs(gold_dir, exist_ok=True)

    if not os.path.exists(silver_path):
        raise FileNotFoundError(f"Le fichier {silver_path} est introuvable. Exécutez clean_silver.py d'abord.")

    df = pd.read_csv(silver_path)
    # Application du calcul de score et des catégories
    df['risk_score'] = df.apply(calculate_risk_score, axis=1)
    df[['wind_category', 'precip_category', 'temp_category']] = df.apply(categorize_weather, axis=1)

    # Classification du Niveau de Risque global (pour filtres facile sur Streamlit)
    conditions = [
        (df['risk_score'] >= 70),
        (df['risk_score'] >= 35) & (df['risk_score'] < 70),
        (df['risk_score'] < 35)
    ]
    choices = ['Élevé', 'Moyen', 'Faible']
    df['risk_level'] = np.select(conditions, choices, default='Faible')

    # Sauvegarde dans le dossier Gold
    output_path = os.path.join(gold_dir, "weather_risk_gold.csv")
    df.to_csv(output_path, index=False)
    print(f"[Gold] Données Gold générées avec succès dans {output_path}")

if __name__ == "__main__":
    run_gold_pipeline()