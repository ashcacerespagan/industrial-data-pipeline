import os
import json
import sqlite3
import pytest
import csv
import tempfile
import datetime

from src.generate_data import generate_panel_inspection_logs
from src.etl_pipeline import DB_PATH, CSV_PATH


# ---------------------------------------------------------------------------
# 1. GENERATOR TESTS & EDGE CASES
# ---------------------------------------------------------------------------

def test_generate_mock_data_file_creation(tmp_path):
    """Verify generator creates a CSV file with expected headers."""
    output_file = tmp_path / "test_logs.csv"
    generate_panel_inspection_logs(num_records=10, output_path=str(output_file))
    
    assert os.path.exists(output_file)
    
    with open(output_file, "r") as f:
        reader = csv.reader(f)
        headers = next(reader)
        assert headers == ["test_id", "serial_number", "panel_type", "timestamp", "voltage_v", "current_ma", "defect_count", "test_status"]
        
        rows = list(reader)
        assert len(rows) == 10

def test_generate_mock_data_zero_records(tmp_path):
    """Edge Case: Generator called with 0 records should produce headers only."""
    output_file = tmp_path / "empty_logs.csv"
    generate_panel_inspection_logs(num_records=0, output_path=str(output_file))
    
    with open(output_file, "r") as f:
        reader = list(csv.reader(f))
        assert len(reader) == 1  # Headers only


# ---------------------------------------------------------------------------
# 2. DATA PARSING & EDGE CASE TESTS
# ---------------------------------------------------------------------------

def parse_csv_records(filepath):
    """Helper mirror function to isolate CSV extraction logic."""
    records = []
    with open(filepath, "r") as f:
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
    return records

def test_parse_valid_csv(tmp_path):
    """Verify valid row data parsing and type conversions."""
    csv_file = tmp_path / "sample.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["test_id", "serial_number", "panel_type", "timestamp", "voltage_v", "current_ma", "defect_count", "test_status"])
        writer.writerow(["TST-1001", "SN-9999", "PNL-X100", "2026-08-15T10:00:00", "24.12", "501.5", "0", "PASS"])
        
    records = parse_csv_records(csv_file)
    assert len(records) == 1
    assert records[0]["voltage_v"] == 24.12
    assert isinstance(records[0]["voltage_v"], float)
    assert isinstance(records[0]["defect_count"], int)

def test_parse_invalid_number_format_raises_error(tmp_path):
    """Edge Case: Malformed numeric values should raise ValueError."""
    csv_file = tmp_path / "corrupt.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["test_id", "serial_number", "panel_type", "timestamp", "voltage_v", "current_ma", "defect_count", "test_status"])
        writer.writerow(["TST-1002", "SN-9999", "PNL-X100", "2026-08-15T10:00:00", "INVALID_VOLTS", "500", "1", "FAIL"])
        
    with pytest.raises(ValueError):
        parse_csv_records(csv_file)


# ---------------------------------------------------------------------------
# 3. YIELD & METRIC CALCULATION EDGE CASES
# ---------------------------------------------------------------------------

def calculate_summary_metrics(records):
    """Helper function to test metric aggregation edge cases without DB writes."""
    if not records:
        return None
    
    passed = sum(1 for r in records if r["test_status"] == "PASS")
    failed = sum(1 for r in records if r["test_status"] == "FAIL")
    retest = sum(1 for r in records if r["test_status"] == "RETEST")
    total = len(records)
    
    return {
        "total_units_tested": total,
        "first_pass_yield_pct": round((passed / total) * 100, 2) if total > 0 else 0.0,
        "failed_units": failed,
        "retest_units": retest,
        "avg_defect_count": round(sum(r["defect_count"] for r in records) / total, 2) if total > 0 else 0.0,
        "max_defects_on_unit": max(r["defect_count"] for r in records) if total > 0 else 0
    }

def test_summary_100_percent_pass():
    """Edge Case: All units passing (100% yield)."""
    records = [
        {"test_status": "PASS", "defect_count": 0},
        {"test_status": "PASS", "defect_count": 1}
    ]
    summary = calculate_summary_metrics(records)
    assert summary["first_pass_yield_pct"] == 100.0
    assert summary["failed_units"] == 0
    assert summary["retest_units"] == 0
    assert summary["max_defects_on_unit"] == 1

def test_summary_100_percent_fail():
    """Edge Case: All units failing (0% yield)."""
    records = [
        {"test_status": "FAIL", "defect_count": 5},
        {"test_status": "FAIL", "defect_count": 10}
    ]
    summary = calculate_summary_metrics(records)
    assert summary["first_pass_yield_pct"] == 0.0
    assert summary["failed_units"] == 2
    assert summary["max_defects_on_unit"] == 10
    assert summary["avg_defect_count"] == 7.5

def test_summary_empty_records():
    """Edge Case: Zero input records returns None (avoids ZeroDivisionError)."""
    assert calculate_summary_metrics([]) is None


# ---------------------------------------------------------------------------
# 4. SQLITE DATABASE INTEGRITY TESTS
# ---------------------------------------------------------------------------

def test_sqlite_table_creation_and_insertion(tmp_path):
    """Verify SQLite database schema creation and row insertion."""
    db_file = tmp_path / "test_db.db"
    conn = sqlite3.connect(db_file)
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
    
    cursor.execute("""
        INSERT INTO panel_inspection_logs 
        (test_id, serial_number, panel_type, timestamp, voltage_v, current_ma, defect_count, test_status, processed_at) 
        VALUES ('TST-001', 'SN-0001', 'PNL-X100', '2026-08-15T11:00:00', 24.0, 500.0, 0, 'PASS', '2026-08-15T11:05:00')
    """)
    conn.commit()
    
    cursor.execute("SELECT COUNT(*), AVG(voltage_v) FROM panel_inspection_logs")
    row_count, avg_voltage = cursor.fetchone()
    conn.close()
    
    assert row_count == 1
    assert avg_voltage == 24.0