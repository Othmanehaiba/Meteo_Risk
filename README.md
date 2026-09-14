# Weather Delivery Pipeline

Pipeline de donnees meteo pour analyser le risque de livraison.

## Architecture

1. **Bronze** : lecture de `ma.csv` et reponses brutes Open-Meteo.
2. **Silver** : nettoyage, typage, dedoublonnage et jointure.
3. **Gold** : calcul du Weather Risk Score et preparation analytique.
4. **PostgreSQL** : stockage des tables finales et requetes metier.
5. **Streamlit** : dashboard de suivi des risques.
6. **Airflow** : orchestration des etapes du pipeline.

Voir `docker-compose.yml` pour demarrer l'environnement local.
