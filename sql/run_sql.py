"""
Helper script to execute schema, seed data, and run all reports in SQLite.
Usage:
    python sql/run_sql.py
"""
import sqlite3
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "mamaearth.db"
SQL_DIR = ROOT / "sql"
DATA_DIR = ROOT / "data"

def init_db():
    print("=" * 65)
    print("STEP 1: Initializing Schema (sql/schema.sql)")
    print("=" * 65)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    schema_sql = (SQL_DIR / "schema.sql").read_text(encoding="utf-8")
    cursor.executescript(schema_sql)
    print("Schema applied successfully.\n")

    print("=" * 65)
    print("STEP 2: Loading Seed Data (data/*.csv)")
    print("=" * 65)
    def load_table(csv_file, table_name):
        with open(DATA_DIR / csv_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
            placeholders = ", ".join(["?"] * len(headers))
            col_str = ", ".join(headers)
            sql = f"INSERT INTO {table_name} ({col_str}) VALUES ({placeholders})"
            rows = []
            for row in reader:
                # Convert empty strings to None so they store as SQL NULL
                cleaned = [None if cell.strip() == "" else cell for cell in row]
                rows.append(cleaned)
            cursor.executemany(sql, rows)
            print(f"Loaded {len(rows)} records into '{table_name}' table.")

    load_table("customers.csv", "customers")
    load_table("products.csv", "products")
    load_table("orders.csv", "orders")
    conn.commit()

    # Verification counts
    cursor.execute("""
        SELECT 'customers' AS tbl, COUNT(*) AS cnt FROM customers
        UNION ALL
        SELECT 'products', COUNT(*) FROM products
        UNION ALL
        SELECT 'orders', COUNT(*) FROM orders;
    """)
    print("\nRow Count Verification:")
    for tbl, cnt in cursor.fetchall():
        print(f"  - {tbl}: {cnt} rows")

    print("\n" + "=" * 65)
    print("STEP 3: Executing SQL Reports (sql/reports.sql)")
    print("=" * 65)

    reports_content = (SQL_DIR / "reports.sql").read_text(encoding="utf-8")
    
    # Extract queries and their preceding comment headers
    # We strip empty lines and split by semicolon
    raw_statements = [s.strip() for s in reports_content.split(";") if s.strip()]

    for i, raw_stmt in enumerate(raw_statements, 1):
        lines = raw_stmt.splitlines()
        # Find comments describing the task
        task_label = f"Query {i}"
        for line in lines:
            if line.strip().startswith("-- Task") or line.strip().startswith("-- Method") or line.strip().startswith("-- Query"):
                task_label = line.strip().lstrip("-").strip()
                break
        
        # Execute only non-comment SQL code
        sql_lines = [l for l in lines if not l.strip().startswith("--")]
        exec_sql = "\n".join(sql_lines).strip()
        if not exec_sql:
            continue

        print(f"\n>>> {task_label} <<<")
        try:
            cursor.execute(exec_sql)
            if cursor.description:
                cols = [desc[0] for desc in cursor.description]
                print(" | ".join(cols))
                print("-" * 45)
                for row in cursor.fetchall():
                    print(" | ".join(str(val) for val in row))
            else:
                conn.commit()
                print("(Statement executed successfully)")
        except Exception as e:
            print(f"Error executing statement: {e}")

    conn.close()
    print("\n" + "=" * 65)
    print("All SQL reports executed successfully!")
    print("=" * 65)

if __name__ == "__main__":
    init_db()
