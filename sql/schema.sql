-- Raw Sensor Logs Staging Table
CREATE TABLE IF NOT EXISTS staging_sensor_logs (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50),
    timestamp TIMESTAMP,
    raw_reading NUMERIC,
    status_code VARCHAR(10),
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Aggregated Metrics Target Table
CREATE TABLE IF NOT EXISTS processed_sensor_metrics (
    metric_id SERIAL PRIMARY KEY,
    device_id VARCHAR(50),
    window_start TIMESTAMP,
    avg_reading NUMERIC(10, 2),
    max_reading NUMERIC(10, 2),
    error_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);