import pandas as pd
import numpy as np
import datetime
import os

def generate_mock_sensor_logs(num_records=500, output_path="data/raw_sensor_logs.csv"):
    """Generate mock industrial sensor log data and save to CSV."""
    print(f"[Generator] Creating {num_records} mock sensor records...")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    np.random.seed(42)
    devices = [f"SENSOR_{i:03d}" for i in range(1, 6)]
    status_options = ["OK", "OK", "OK", "OK", "WARN", "ERR"]
    
    start_time = datetime.datetime.now() - datetime.timedelta(days=1)
    timestamps = [start_time + datetime.timedelta(minutes=np.random.randint(0, 1440)) for _ in range(num_records)]
    
    data = {
        "device_id": np.random.choice(devices, size=num_records),
        "timestamp": sorted(timestamps),
        "raw_reading": np.round(np.random.normal(loc=75.0, scale=12.5, size=num_records), 2),
        "status_code": np.random.choice(status_options, size=num_records)
    }
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"[Generator] Saved raw data to {output_path}")

if __name__ == "__main__":
    generate_mock_sensor_logs()