import csv
import sqlite3
import json
import datetime
import os

DB_PATH = "data/industrial_data.db"
CSV_PATH = "data/panel_test_logs.csv"

# 1. READ CSV LOGS
print("1. Reading raw panel inspection logs...")
records = []
with open(CSV_PATH, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        records.append({
            "test_id": row["test_id"],
            "serial_number": row["serial_number"],
            "panel_type": row["panel_type"],
            "timestamp": row["timestamp"],
            "voltage_v": float(row["voltage_v"]),
            "current_ma": float(row["current_ma"]),
            "defect_count": int(row["defect_count"]),
            "test_status": row["test_status"]
        })

# 2. SAVE TO SQLITE DATABASE
print("2. Saving records to SQLite database...")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS panel_inspection_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_id TEXT,
        serial_number TEXT,
        panel_type TEXT,
        timestamp TEXT,
        voltage_v REAL,
        current_ma REAL,
        defect_count INTEGER,
        test_status TEXT,
        processed_at TEXT
    )
""")

now = datetime.datetime.now().isoformat()
for r in records:
    cursor.execute("""
        INSERT INTO panel_inspection_logs 
        (test_id, serial_number, panel_type, timestamp, voltage_v, current_ma, defect_count, test_status, processed_at) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (r["test_id"], r["serial_number"], r["panel_type"], r["timestamp"], 
          r["voltage_v"], r["current_ma"], r["defect_count"], r["test_status"], now))

conn.commit()
conn.close()

# 3. EXPORT JSON QUALITY SUMMARY
print("3. Exporting inspection quality summary...")
if records:
    passed = sum(1 for r in records if r["test_status"] == "PASS")
    failed = sum(1 for r in records if r["test_status"] == "FAIL")
    retest = sum(1 for r in records if r["test_status"] == "RETEST")
    total = len(records)
    
    summary = {
        "run_timestamp": now,
        "total_units_tested": total,
        "first_pass_yield_pct": round((passed / total) * 100, 2),
        "failed_units": failed,
        "retest_units": retest,
        "avg_defect_count": round(sum(r["defect_count"] for r in records) / total, 2),
        "max_defects_on_unit": max(r["defect_count"] for r in records)
    }
    
    os.makedirs("data", exist_ok=True)
    with open("data/latest_inspection_run.json", "w") as f:
        json.dump(summary, f, indent=4)

print("Inspection ETL pipeline completed successfully!")