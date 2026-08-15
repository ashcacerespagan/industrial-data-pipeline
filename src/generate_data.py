import csv
import random
import datetime
import os

def generate_panel_inspection_logs(num_records=150, output_path="data/panel_test_logs.csv"):
    print(f"Generating {num_records} panel test inspection records...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    panel_types = ["PNL-X100", "PNL-X200", "PNL-X300"]
    statuses = ["PASS", "PASS", "PASS", "PASS", "FAIL", "RETEST"]
    
    start_time = datetime.datetime.now() - datetime.timedelta(days=1)
    
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["test_id", "serial_number", "panel_type", "timestamp", "voltage_v", "current_ma", "defect_count", "test_status"])
        
        for i in range(1, num_records + 1):
            test_id = f"TST-{1000 + i}"
            serial_number = f"SN-2026-{random.randint(10000, 99999)}"
            panel_type = random.choice(panel_types)
            timestamp = (start_time + datetime.timedelta(minutes=i * 10)).isoformat()
            voltage = round(random.uniform(23.5, 24.5), 2)
            current = round(random.uniform(480.0, 520.0), 1)
            status = random.choice(statuses)
            
            # Higher defect count if test failed
            defect_count = random.randint(3, 12) if status in ["FAIL", "RETEST"] else random.randint(0, 2)
            
            writer.writerow([test_id, serial_number, panel_type, timestamp, voltage, current, defect_count, status])
            
    print(f"Saved panel test logs to {output_path}")

if __name__ == "__main__":
    generate_panel_inspection_logs()