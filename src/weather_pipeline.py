import sqlite3
import json
import datetime
import requests

# 1. FETCH LIVE DATA FROM NWS API
print("1. Fetching live data from National Weather Service...")
url = "https://api.weather.gov/stations/KCOS/observations"
headers = {"User-Agent": "WeatherApp/1.0"}

response = requests.get(url, headers=headers)
data = response.json()

# Extract observations list
observations = data.get("features", [])

# 2. CLEAN & PROCESS OBSERVATIONS
print("2. Processing observations...")
cleaned_records = []

for item in observations:
    props = item.get("properties", {})
    temp_c = props.get("temperature", {}).get("value")
    
    # Skip records missing a temperature reading
    if temp_c is None:
        continue
        
    temp_f = round((temp_c * 9/5) + 32, 1)
    timestamp = props.get("timestamp")
    humidity = props.get("relativeHumidity", {}).get("value")
    
    cleaned_records.append((timestamp, temp_f, humidity))

# 3. SAVE TO SQLITE DATABASE (HISTORICAL STORE)
print("3. Saving to SQLite database...")
conn = sqlite3.connect("data/industrial_data.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        temp_f REAL,
        humidity REAL,
        created_at TEXT
    )
""")

now = datetime.datetime.now().isoformat()
for record in cleaned_records:
    cursor.execute(
        "INSERT INTO weather_logs (timestamp, temp_f, humidity, created_at) VALUES (?, ?, ?, ?)",
        (record[0], record[1], record[2], now)
    )

conn.commit()
conn.close()

# 4. SAVE SUMMARY TO JSON (GIT-TRACKED)
print("4. Saving JSON summary...")
if cleaned_records:
    temps = [r[1] for r in cleaned_records]
    summary = {
        "last_updated": now,
        "total_readings": len(cleaned_records),
        "latest_temp_f": cleaned_records[0][1],
        "max_temp_f": max(temps),
        "min_temp_f": min(temps)
    }

    with open("data/latest_weather_run.json", "w") as f:
        json.dump(summary, f, indent=4)

print("Pipeline finished successfully!")