import pandas as pd
import sqlite3

DB_PATH = "data/industrial_data.db"

def get_top_performing_devices(limit=3):
    """Retrieve devices with the highest average readings."""
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT device_id, 
               ROUND(AVG(avg_reading), 2) AS overall_avg,
               MAX(max_reading) AS peak_reading
        FROM processed_sensor_metrics
        GROUP BY device_id
        ORDER BY overall_avg DESC
        LIMIT ?;
    """
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df

def get_anomaly_report():
    """Identify devices recording high peak metrics or status flags."""
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT device_id, window_start, max_reading
        FROM processed_sensor_metrics
        WHERE max_reading > 95.0
        ORDER BY max_reading DESC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

if __name__ == "__main__":
    print("--- Top Performing Devices ---")
    print(get_top_performing_devices())
    print("\n--- High Reading Anomaly Report ---")
    print(get_anomaly_report())