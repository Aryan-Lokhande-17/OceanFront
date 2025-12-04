import duckdb
import os
from pathlib import Path

# Check all parquet files
data_path = Path("oceanFrontData/Parquet")
parquet_files = sorted(data_path.glob("*.parquet"))

print(f"Found {len(parquet_files)} Parquet files:\n")

total_all = 0
for idx, pfile in enumerate(parquet_files):
    conn = duckdb.connect(':memory:')
    conn.execute(f'CREATE TABLE t AS SELECT * FROM read_parquet("{pfile}")')
    
    count = conn.execute('SELECT COUNT(*) FROM t').fetchone()[0]
    unique_plat = conn.execute('SELECT COUNT(DISTINCT platform_number) FROM t').fetchone()[0]
    
    print(f"{idx}. {pfile.name}")
    print(f"   Rows: {count}, Unique platforms: {unique_plat}")
    
    # Show platform distribution
    plats = conn.execute('SELECT platform_number, COUNT(*) FROM t GROUP BY platform_number ORDER BY COUNT(*) DESC LIMIT 3').fetchall()
    for plat, cnt in plats:
        print(f"     - {plat}: {cnt} rows")
    
    total_all += count
    print()

print(f"TOTAL ACROSS ALL FILES: {total_all} rows")
print("\nWe should be using UNION or APPEND of ALL 5 files, not just the first one!")
