import pandas as pd
from sqlalchemy import create_engine
import datetime
import json
import os

DB_PATH = "sqlite:///data/industrial_data.db"

def extract_data(filepath: str) -> pd.DataFrame:
    """Extract raw sensor data from CSV log files."""
    print(f"[Extract] Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean data and calculate aggregated device metrics."""
    print("[Transform] Cleaning and aggregating sensor metrics...")
    
    valid_df = df[df['status_code'] == 'OK'].copy()
    valid_df['window_start'] = valid_df['timestamp'].dt.floor('h')
    
    transformed = valid_df.groupby(['device_id', 'window_start']).agg(
        avg_reading=('raw_reading', 'mean'),
        max_reading=('raw_reading', 'max')
    ).reset_index()
    
    # Track historical insertion timestamp
    transformed['created_at'] = datetime.datetime.now().isoformat()
    return transformed

def load_data(df: pd.DataFrame, db_engine) -> None:
    """Append transformed metrics into SQLite database."""
    print("[Load] Appending metrics to 'processed_sensor_metrics' table...")
    df.to_sql('processed_sensor_metrics', db_engine, if_exists='append', index=False)

def export_json_summary(df: pd.DataFrame, output_path="data/latest_run.json") -> None:
    """Export the current run's summary for Git tracking and diffs."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    summary = {
        "run_timestamp": datetime.datetime.now().isoformat(),
        "total_records_processed": len(df),
        "devices_monitored": df['device_id'].nunique(),
        "overall_avg_reading": round(df['avg_reading'].mean(), 2),
        "peak_reading": round(df['max_reading'].max(), 2),
        "metrics_preview": df.head(5).to_dict(orient="records")
    }
    
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=4)
        
    print(f"[Export] Saved latest run summary to {output_path}")

if __name__ == "__main__":
    engine = create_engine(DB_PATH)
    raw_csv = "data/raw_sensor_logs.csv"
    
    raw_df = extract_data(raw_csv)
    transformed_df = transform_data(raw_df)
    
    # Store history in SQLite & export diffable JSON
    load_data(transformed_df, engine)
    export_json_summary(transformed_df)
    print("[Success] Pipeline completed successfully.")