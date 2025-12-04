"""
Query Executor using DuckDB and Parquet files
Executes SQL queries on oceanographic data
"""

import duckdb
import os
from pathlib import Path
from config import config
import polars as pl

class QueryExecutor:
    """Execute SQL queries on Parquet datasets using DuckDB"""
    
    def __init__(self):
        self.data_path = Path(config.PARQUET_DATA_PATH)
        self.connection = duckdb.connect(':memory:')  # In-memory database
        self.parquet_files = []  # Store parquet file paths
        self._load_parquet_files()  # Load real Parquet data
    
    def _load_parquet_files(self):
        """Load ALL Parquet files with ALL columns - no transformations"""
        try:
            if not self.data_path.exists():
                print(f"[!] Data path does not exist: {self.data_path}")
                self._create_sample_data()
                return
            
            parquet_files = list(self.data_path.glob("*.parquet"))
            if not parquet_files:
                print("[!] No Parquet files found")
                self._create_sample_data()
                return
            
            print(f"[>>] Found {len(parquet_files)} Parquet files")
            self.parquet_files = parquet_files
            
            # Count total records
            total_records = 0
            for parquet_file in parquet_files:
                try:
                    count = self.connection.execute(f"SELECT COUNT(*) FROM read_parquet('{parquet_file}')").fetchone()[0]
                    total_records += count
                    print(f"[>>] {parquet_file.name}: {count} records")
                except Exception as e:
                    print(f"[!] Error reading {parquet_file.name}: {e}")
            
            # Create buoy_data table by loading all parquet files
            # Load each file separately to avoid UNION ALL type casting issues
            try:
                # Start with first file
                self.connection.execute(f"""
                    CREATE TABLE buoy_data AS
                    SELECT * FROM read_parquet('{parquet_files[0]}')
                """)
                
                # Append remaining files
                for parquet_file in parquet_files[1:]:
                    self.connection.execute(f"""
                        INSERT INTO buoy_data
                        SELECT * FROM read_parquet('{parquet_file}')
                    """)
                
                print(f"[OK] Created buoy_data with all records")
            except Exception as e:
                print(f"[!] Error creating buoy_data: {e}")
            
            print(f"[OK] Total records: {total_records}")
            
            # Get column names for debugging
            columns_result = self.connection.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'buoy_data'
                ORDER BY ordinal_position
            """).fetchall()
            available_columns = [col[0] for col in columns_result]
            print(f"[OK] Available columns ({len(available_columns)}): {', '.join(available_columns[:8])}...")
            
            # Create a location_info summary table (safe column selection)
            try:
                self.connection.execute("""
                    CREATE TABLE location_info AS
                    SELECT DISTINCT
                        platform_number,
                        latitude,
                        longitude,
                        temp,
                        psal,
                        pres,
                        'Argo Profile' as data_type
                    FROM buoy_data
                    WHERE platform_number IS NOT NULL
                """)
                
                loc_count = self.connection.execute("SELECT COUNT(*) FROM location_info").fetchone()[0]
                print(f"[OK] location_info: {loc_count} unique profiles")
            except Exception as e:
                print(f"[!] Could not create location_info: {e}")
            
        except Exception as e:
            print(f"[ERROR] Error loading Parquet files: {e}")
            print("       Falling back to sample data...")
            self._create_sample_data()
    
    def _create_sample_data(self):
        """Create sample oceanographic data for demonstration"""
        print("[*] Creating sample oceanographic data...")
        
        try:
            # Drop existing tables if they exist (fresh start)
            try:
                self.connection.execute("DROP TABLE IF EXISTS buoy_data")
                self.connection.execute("DROP TABLE IF EXISTS location_info")
            except:
                pass
            
            # Sample buoy data - create table directly with INSERT
            self.connection.execute("""
                CREATE TABLE buoy_data (
                    buoy_id TEXT,
                    buoy_name TEXT,
                    latitude FLOAT,
                    longitude FLOAT,
                    timestamp TIMESTAMP,
                    sst FLOAT,
                    salinity FLOAT,
                    wind_speed FLOAT,
                    wind_direction FLOAT,
                    wave_height FLOAT,
                    wave_period FLOAT,
                    pressure FLOAT,
                    current_speed FLOAT
                )
            """)
            
            # Insert sample data
            self.connection.execute("""
                INSERT INTO buoy_data VALUES
                ('IMBA-01', 'Kochi', 9.98, 76.30, '2025-12-04 10:00:00', 28.5, 35.2, 5.2, 120, 0.8, 5.2, 1013.2, 0.3),
                ('IMBA-02', 'Visakhapatnam', 17.70, 83.22, '2025-12-04 10:15:00', 27.2, 34.8, 4.8, 145, 1.2, 6.1, 1012.8, 0.4),
                ('IMBA-04', 'Chennai', 13.05, 80.28, '2025-12-04 10:30:00', 29.1, 35.0, 6.1, 110, 1.0, 5.8, 1013.5, 0.25),
                ('46045', 'Arabian Sea', 13.30, 73.70, '2025-12-04 10:45:00', 28.0, 35.1, 3.9, 130, 0.6, 4.5, 1014.0, 0.2),
                ('46046', 'Bay of Bengal', 12.15, 80.45, '2025-12-04 11:00:00', 26.8, 34.9, 5.5, 140, 1.5, 6.5, 1012.5, 0.35)
            """)
            
            # Create location info - ALWAYS ensure this table exists
            self.connection.execute("""
                CREATE TABLE location_info AS
                SELECT DISTINCT
                    buoy_id,
                    buoy_name,
                    latitude,
                    longitude,
                    CASE 
                        WHEN longitude < 74 THEN 'West Coast'
                        WHEN longitude BETWEEN 74 AND 84 THEN 'East Coast'
                        WHEN latitude < 8 THEN 'South'
                        ELSE 'Arabian Sea'
                    END as coast,
                    CASE
                        WHEN buoy_id LIKE 'IMBA%' THEN 'IMBA'
                        WHEN buoy_id LIKE '4%' THEN 'NOAA NDBC'
                        ELSE 'Other'
                    END as operator,
                    'India Meteorological Data Portal' as data_portal
                FROM buoy_data
                ORDER BY buoy_id
            """)
            
            # Verify both tables exist
            tables = self.connection.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_type = 'BASE TABLE'
            """).fetchall()
            table_names = [t[0] for t in tables]
            print(f"[OK] Created tables: {', '.join(table_names)}")
            
        except Exception as e:
            print(f"[ERROR] Error creating sample data: {e}")
            import traceback
            traceback.print_exc()
    
    def execute(self, sql_query: str) -> dict:
        """
        Execute SQL query and return results
        
        Args:
            sql_query: Valid DuckDB SQL query
        
        Returns:
            dict with keys:
                - success: bool
                - data: list of dicts (query results)
                - columns: list of column names
                - row_count: number of rows returned
                - error: error message if failed
        """
        try:
            # Sanitize and validate query (basic protection)
            if any(keyword in sql_query.upper() for keyword in ['DROP', 'DELETE', 'INSERT', 'UPDATE']):
                return {
                    "success": False,
                    "error": "Only SELECT queries are allowed",
                    "data": [],
                    "columns": [],
                    "row_count": 0
                }
            
            # Execute query
            result = self.connection.execute(sql_query).fetchall()
            columns = [desc[0] for desc in self.connection.description] if self.connection.description else []
            
            # Convert to list of dicts and clean up bytes
            data = []
            for row in result:
                row_dict = {}
                for col, val in zip(columns, row):
                    # Decode bytes to string
                    if isinstance(val, bytes):
                        row_dict[col] = val.decode('utf-8', errors='ignore').strip()
                    else:
                        row_dict[col] = val
                data.append(row_dict)
            
            return {
                "success": True,
                "data": data,
                "columns": columns,
                "row_count": len(data),
                "error": None
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Query execution failed: {str(e)}",
                "data": [],
                "columns": [],
                "row_count": 0
            }


# Singleton instance
query_executor = QueryExecutor()
