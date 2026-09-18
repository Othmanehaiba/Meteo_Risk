from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

# Ajout du répertoire racine d'Airflow au PYTHONPATH
sys.path.append("/opt/airflow")

# Importation des fonctions de chaque étape du pipeline
from extraction.extract_weather import run_extraction
from transformation.clean_silver import run_silver_pipeline
from transformation.feature_gold import run_gold_pipeline
from load.load_postgres import load_gold_to_postgres

# Configuration des paramètres par défaut du DAG
default_args = {
    'owner': 'meteorisk',
    'depends_on_past': False,
    'start_date': datetime(2026, 9, 1),
    'email_on_failure': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

# Définition du DAG Airflow
with DAG(
    'meteorisk_pipeline_v1',
    default_args=default_args,
    description='Pipeline ETL quotidien pour l\'évaluation des risques météo logistiques au Maroc',
    schedule_interval='0 6 * * *',  # Exécution automatique tous les jours à 06h00
    catchup=False
) as dag:

    # 1. Tâche d'extraction (Bronze)
    task_extract = PythonOperator(
        task_id='extract_bronze',
        python_callable=run_extraction
    )

    # 2. Tâche de nettoyage (Silver)
    task_silver = PythonOperator(
        task_id='clean_silver',
        python_callable=run_silver_pipeline
    )

    # 3. Tâche de feature engineering (Gold)
    task_gold = PythonOperator(
        task_id='feature_gold',
        python_callable=run_gold_pipeline
    )

    # 4. Tâche de chargement dans PostgreSQL
    task_load = PythonOperator(
        task_id='load_postgres',
        python_callable=load_gold_to_postgres
    )

    # Définition de l'ordre séquentiel d'exécution
    task_extract >> task_silver >> task_gold >> task_load