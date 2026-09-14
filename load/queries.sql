-- 1. Risque moyen par categorie
SELECT risk_category, AVG(risk_score) AS average_risk
FROM weather_risk
GROUP BY risk_category
ORDER BY average_risk DESC;

-- 2. Livraisons les plus risquees
SELECT * FROM weather_risk
ORDER BY risk_score DESC
LIMIT 20;

-- 3. Risque moyen par jour
SELECT delivery_date, AVG(risk_score) AS average_risk
FROM weather_risk
GROUP BY delivery_date
ORDER BY delivery_date;

-- 4. Repartition des categories
SELECT risk_category, COUNT(*) AS deliveries
FROM weather_risk
GROUP BY risk_category
ORDER BY deliveries DESC;

-- 5. Score maximum par zone
SELECT latitude, longitude, MAX(risk_score) AS maximum_risk
FROM weather_risk
GROUP BY latitude, longitude
ORDER BY maximum_risk DESC;
