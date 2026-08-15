import sqlite3
import argparse

DB_PATH = "data/industrial_data.db"

def get_yield_by_panel_type(status_filter=None):
    """Calculate pass/fail totals by panel model, optionally filtered by status."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if status_filter:
        query = """
            SELECT panel_type,
                   COUNT(*) AS total_tested,
                   SUM(CASE WHEN test_status = 'PASS' THEN 1 ELSE 0 END) AS passed,
                   SUM(CASE WHEN test_status = 'FAIL' THEN 1 ELSE 0 END) AS failed,
                   ROUND(AVG(defect_count), 2) AS avg_defects
            FROM panel_inspection_logs
            WHERE test_status = ?
            GROUP BY panel_type;
        """
        cursor.execute(query, (status_filter.upper(),))
    else:
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

def get_filtered_inspection_units(status=None, panel_type=None, limit=5):
    """Retrieve specific inspection logs based on panel status or model."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    conditions = []
    params = []
    
    if status:
        conditions.append("test_status = ?")
        params.append(status.upper())
    if panel_type:
        conditions.append("panel_type = ?")
        params.append(panel_type.upper())
        
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"""
        SELECT test_id, serial_number, panel_type, defect_count, voltage_v, current_ma, test_status
        FROM panel_inspection_logs
        {where_clause}
        ORDER BY defect_count DESC
        LIMIT ?;
    """
    params.append(limit)
    
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    return rows

def main():
    parser = argparse.ArgumentParser(description="Query hardware panel inspection telemetry logs.")
    parser.add_argument("--status", type=str, choices=["PASS", "FAIL", "RETEST"], help="Filter logs by test status")
    parser.add_argument("--model", type=str, help="Filter logs by panel model (e.g., PNL-X100)")
    parser.add_argument("--limit", type=int, default=5, help="Number of records to display (default: 5)")
    
    args = parser.parse_args()
    
    print("\n--- Panel Inspection Telemetry Report ---")
    if args.status or args.model:
        print(f"Filters Applied -> Status: {args.status or 'ALL'} | Model: {args.model or 'ALL'}")
        
    print("\n[Yield Metrics by Panel Model]")
    yield_data = get_yield_by_panel_type(args.status)
    if yield_data:
        for row in yield_data:
            print(f"Model: {row[0]} | Total: {row[1]} | Passed: {row[2]} | Failed: {row[3]} | Avg Defects: {row[4]}")
    else:
        print("No matching aggregate records found.")
        
    print(f"\n[Filtered Inspection Records (Top {args.limit})]")
    records = get_filtered_inspection_units(status=args.status, panel_type=args.model, limit=args.limit)
    if records:
        for r in records:
            print(f"Test ID: {r[0]} | SN: {r[1]} | Model: {r[2]} | Defects: {r[3]} | V: {r[4]} | mA: {r[5]} | Status: {r[6]}")
    else:
        print("No matching inspection records found.")

if __name__ == "__main__":
    main()