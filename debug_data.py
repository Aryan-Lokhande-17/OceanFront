import duckdb
import os

conn = duckdb.connect(':memory:')

# Load the first Parquet file
parquet_path = "oceanFrontData/Parquet/nodc_R1901514_311.parquet"
print(f"Checking: {parquet_path}")
print(f"File exists: {os.path.exists(parquet_path)}")

conn.execute(f'CREATE TABLE bd AS SELECT * FROM read_parquet("{parquet_path}")')

# Total rows
total = conn.execute('SELECT COUNT(*) FROM bd').fetchone()[0]
print(f"\nTotal rows: {total}")

# Unique platforms
uniq_plat = conn.execute('SELECT COUNT(DISTINCT platform_number) FROM bd').fetchone()[0]
print(f"Unique platforms: {uniq_plat}")

# Check platform breakdown
platforms = conn.execute('SELECT DISTINCT platform_number, COUNT(*) as cnt FROM bd GROUP BY platform_number').fetchall()
print("\nPlatform breakdown:")
for plat, cnt in platforms:
    print(f"  Platform: {plat} → {cnt} rows")

# Check temperature data
temp_count = conn.execute('SELECT COUNT(*) FROM bd WHERE temp IS NOT NULL').fetchone()[0]
print(f"\nRows with temperature data: {temp_count}")

# Sample data
print("\nSample rows (temp, pres, platform):")
samples = conn.execute('SELECT temp, pres, platform_number FROM bd WHERE temp IS NOT NULL LIMIT 10').fetchall()
for temp, pres, plat in samples:
    print(f"  temp={temp}, pres={pres}, platform={plat}")
