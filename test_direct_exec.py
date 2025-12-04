#!/usr/bin/env python
"""Test direct query execution"""

import sys
sys.path.insert(0, 'd:\\EDAI\\OceanFront\\backend')

from services.query_executor import query_executor

sql = "SELECT DISTINCT CAST(platform_number AS VARCHAR) AS platform, ROUND(CAST(temp AS FLOAT), 2) AS temperature FROM buoy_data WHERE temp IS NOT NULL LIMIT 100"

print("=" * 60)
print("TESTING DIRECT QUERY EXECUTION")
print("=" * 60)
print(f"\nSQL: {sql}")

result = query_executor.execute(sql)

print(f"\nSuccess: {result['success']}")
print(f"Row count: {result['row_count']}")
print(f"Error: {result.get('error')}")

if result['success'] and result['data']:
    print(f"\nFirst 3 rows:")
    for row in result['data'][:3]:
        print(f"  {row}")
