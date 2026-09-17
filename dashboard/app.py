import streamlit as st
import pandas as pd
import plotly.express as px
from db import load_data

# Configuration de la page Streamlit
st.set_page_config(
    page_title="MétéoRisk Maroc - Décision Logistique",
    page_icon="🚚",
    layout="wide"
)

st.title("🚚 MétéoRisk — Anticipation des Perturbations Logistiques au Maroc")
st.markdown("Plateforme d'aide à la décision pour l'optimisation des trajets de livraison.")

# 1. Chargement des données
try:
    df = load_data()
except Exception as e:
    st.error(f"Erreur de connexion à la base de données PostgreSQL : {e}")
    st.stop()

# 2. Barre latérale : Filtres dynamiques
st.sidebar.header("🔍 Filtres Opérationnels")

# Filtre par Ville
villes_dispo = ["Toutes"] + sorted(list(df["nom_ville"].dropna().unique()))
ville_selected = st.sidebar.selectbox("Sélectionner une ville :", villes_dispo)

# Filtre par Niveau de Risque
risques_dispo = ["Tous"] + sorted(list(df["risk_level"].dropna().unique()))
risque_selected = st.sidebar.selectbox("Niveau de risque :", risques_dispo)

# Filtre par Plage de Dates
min_date = pd.to_datetime(df["date_prevision"]).min().date()
max_date = pd.to_datetime(df["date_prevision"]).max().date()
date_range = st.sidebar.date_input("Période :", [min_date, max_date], min_value=min_date, max_value=max_date)

# Filtrage du DataFrame selon les choix
df_filtered = df.copy()
df_filtered["date_prevision"] = pd.to_datetime(df_filtered["date_prevision"]).dt.date

if ville_selected != "Toutes":
    df_filtered = df_filtered[df_filtered["nom_ville"] == ville_selected]

if risque_selected != "Tous":
    df_filtered = df_filtered[df_filtered["risk_level"] == risque_selected]

if len(date_range) == 2:
    df_filtered = df_filtered[
        (df_filtered["date_prevision"] >= date_range[0]) & 
        (df_filtered["date_prevision"] <= date_range[1])
    ]

# 3. Métriques clés (KPIs)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Villes suivies", len(df_filtered["nom_ville"].unique()))
col2.metric("Score de Risque Moyen", f"{df_filtered['risk_score'].mean():.1f} / 100")
col3.metric("Pluie Max (mm)", f"{df_filtered['precipitation'].max():.1f}")
col4.metric("Vent Max (km/h)", f"{df_filtered['wind_speed'].max():.1f}")

st.divider()

# 4. Visualisations principales
tab1, tab2, tab3 = st.tabs(["🌍 Carte des Risques", "📊 Analyses & Tendances", "📋 Données Brutes"])

with tab1:
    st.subheader("Cartographie des Zones à Risque")
    fig_map = px.scatter_map(
        df_filtered,
        lat="latitude",
        lon="longitude",
        color="risk_score",
        size="risk_score",
        hover_name="nom_ville",
        hover_data=["risk_level", "temp_max", "precipitation", "wind_speed"],
        color_continuous_scale="Reds",
        size_max=25,
        zoom=4,
        center={"lat": 31.7917, "lon": -7.0926},
        map_style="carto-positron",
        title="Niveau de risque par ville"
    )
    st.plotly_chart(fig_map, use_container_width=True)

with tab2:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Évolution du Score de Risque dans le temps")
        fig_line = px.line(
            df_filtered,
            x="date_prevision",
            y="risk_score",
            color="nom_ville",
            markers=True,
            title="Score de Risque par Date"
        )
        st.plotly_chart(fig_line, use_container_width=True)

    with col_b:
        st.subheader("Top 5 des Villes les plus à Risque")
        top_villes = df_filtered.groupby("nom_ville")["risk_score"].mean().reset_index()
        top_villes = top_villes.sort_values(by="risk_score", ascending=False).head(5)
        fig_bar = px.bar(
            top_villes,
            x="nom_ville",
            y="risk_score",
            color="risk_score",
            color_continuous_scale="Reds",
            title="Risque Moyen par Ville"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

with tab3:
    st.subheader("Extrait des Données")
    st.dataframe(df_filtered, use_container_width=True)