import csv
import sqlite3
import json
import datetime
import os

DB_PATH = "data/industrial_data.db"
CSV_PATH = "data/raw_sensor_logs.csv"

# 1. READ CSV DATA
print("1. Reading raw CSV logs...")
records = []
with open(CSV_PATH, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        records.append({
            "device_id": row["device_id"],
            "timestamp": row["timestamp"],
            "raw_reading": float(row["raw_reading"]),
            "status_code": row["status_code"]
        })

# 2. SAVE TO SQLITE DATABASE
print("2. Saving records to SQLite database...")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS staging_sensor_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT,
        timestamp TEXT,
        raw_reading REAL,
        status_code TEXT,
        created_at TEXT
    )
""")

now = datetime.datetime.now().isoformat()
for r in records:
    cursor.execute(
        "INSERT INTO staging_sensor_logs (device_id, timestamp, raw_reading, status_code, created_at) VALUES (?, ?, ?, ?, ?)",
        (r["device_id"], r["timestamp"], r["raw_reading"], r["status_code"], now)
    )

conn.commit()
conn.close()

# 3. EXPORT JSON SUMMARY
print("3. Exporting JSON summary...")
if records:
    readings = [r["raw_reading"] for r in records]
    summary = {
        "last_updated": now,
        "total_records": len(records),
        "avg_reading": round(sum(readings) / len(readings), 2),
        "max_reading": max(readings),
        "min_reading": min(readings)
    }
    
    os.makedirs("data", exist_ok=True)
    with open("data/latest_run.json", "w") as f:
        json.dump(summary, f, indent=4)

print("ETL pipeline completed successfully!")