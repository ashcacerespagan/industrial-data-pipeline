import sqlite3

DB_PATH = "data/industrial_data.db"

def get_device_summary():
    """Get average and max reading per device."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
        SELECT device_id, 
               ROUND(AVG(raw_reading), 2) AS avg_reading, 
               MAX(raw_reading) AS peak_reading,
               COUNT(*) AS total_logs
        FROM staging_sensor_logs
        GROUP BY device_id;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_warnings_and_errors():
    """Retrieve logs marked with WARN or ERR status."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
        SELECT device_id, timestamp, raw_reading, status_code
        FROM staging_sensor_logs
        WHERE status_code IN ('WARN', 'ERR')
        LIMIT 5;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    print("--- Device Performance Summary ---")
    for row in get_device_summary():
        print(f"Device: {row[0]} | Avg: {row[1]} | Peak: {row[2]} | Logs: {row[3]}")
        
    print("\n--- Recent Warnings / Errors ---")
    for row in get_warnings_and_errors():
        print(f"Device: {row[0]} | Time: {row[1]} | Value: {row[2]} | Status: {row[3]}")