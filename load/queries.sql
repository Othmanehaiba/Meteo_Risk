-- Requête 1 : Villes avec les températures maximales les plus élevées
SELECT nom_ville, MAX(temp_max) AS temp_maximale_atteinte
FROM fact_previsions_risques
GROUP BY nom_ville
ORDER BY temp_maximale_atteinte DESC
LIMIT 5;

-- Requête 2 : Villes avec les plus fortes précipitations cumulées
SELECT nom_ville, SUM(precipitation) AS total_precipitations
FROM fact_previsions_risques
GROUP BY nom_ville
ORDER BY total_precipitations DESC
LIMIT 5;

-- Requête 3 : Villes présentant le score de risque moyen le plus élevé
SELECT nom_ville, ROUND(AVG(risk_score)::numeric, 2) AS risque_moyen
FROM fact_previsions_risques
GROUP BY nom_ville
ORDER BY risque_moyen DESC;

-- Requête 4 : Périodes (dates) présentant le risque maximal au niveau national
SELECT date_prevision, ROUND(AVG(risk_score)::numeric, 2) AS risque_moyen_national, MAX(risk_score) AS risque_max_observe
FROM fact_previsions_risques
GROUP BY date_prevision
ORDER BY risque_max_observe DESC;

-- Requête 5 : Pour chaque ville, la journée à risque maximal (Top 1 par ville)
WITH RankedRisks AS (
    SELECT nom_ville, date_prevision, risk_score, risk_level,
           ROW_NUMBER() OVER (PARTITION BY nom_ville ORDER BY risk_score DESC) as rank
    FROM fact_previsions_risques
)
SELECT nom_ville, date_prevision, risk_score, risk_level
FROM RankedRisks
WHERE rank = 1
ORDER BY risk_score DESC;