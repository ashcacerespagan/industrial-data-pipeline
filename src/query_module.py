import sqlite3

DB_PATH = "data/industrial_data.db"

def get_yield_by_panel_type():
    """Calculate pass/fail totals by panel model."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
        SELECT panel_type,
               COUNT(*) AS total_tested,
               SUM(CASE WHEN test_status = 'PASS' THEN 1 ELSE 0 END) AS passed,
               SUM(CASE WHEN test_status = 'FAIL' THEN 1 ELSE 0 END) AS failed,
               ROUND(AVG(defect_count), 2) AS avg_defects
        FROM panel_inspection_logs
        GROUP BY panel_type;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_failed_panel_defects():
    """Retrieve details for failed panels with high defect counts."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
        SELECT test_id, serial_number, panel_type, defect_count, voltage_v, current_ma
        FROM panel_inspection_logs
        WHERE test_status IN ('FAIL', 'RETEST')
        ORDER BY defect_count DESC
        LIMIT 5;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    print("--- Yield Summary by Panel Model ---")
    for row in get_yield_by_panel_type():
        print(f"Model: {row[0]} | Tested: {row[1]} | Passed: {row[2]} | Failed: {row[3]} | Avg Defects: {row[4]}")
        
    print("\n--- Critical Defect Inspection Units ---")
    for row in get_failed_panel_defects():
        print(f"Test ID: {row[0]} | SN: {row[1]} | Model: {row[2]} | Defects: {row[3]} | V: {row[4]} | mA: {row[5]}")