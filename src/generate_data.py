import csv
import random
import datetime
import os

def generate_mock_sensor_logs(num_records=100, output_path="data/raw_sensor_logs.csv"):
    print(f"Generating {num_records} mock sensor records...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    devices = ["SENSOR_001", "SENSOR_002", "SENSOR_003", "SENSOR_004", "SENSOR_005"]
    statuses = ["OK", "OK", "OK", "WARN", "ERR"]
    
    start_time = datetime.datetime.now() - datetime.timedelta(days=1)
    
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["device_id", "timestamp", "raw_reading", "status_code"])
        
        for i in range(num_records):
            device = random.choice(devices)
            timestamp = (start_time + datetime.timedelta(minutes=i * 15)).isoformat()
            reading = round(random.uniform(60.0, 95.0), 2)
            status = random.choice(statuses)
            writer.writerow([device, timestamp, reading, status])
            
    print(f"Saved mock data to {output_path}")

if __name__ == "__main__":
    generate_mock_sensor_logs()