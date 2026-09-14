CREATE TABLE IF NOT EXISTS weather_risk (
    delivery_id BIGINT PRIMARY KEY,
    delivery_date DATE NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    risk_score NUMERIC(5, 2) NOT NULL,
    risk_category TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
