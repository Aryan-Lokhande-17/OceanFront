#!/usr/bin/env python
"""Test simple queries"""

import sys
sys.path.insert(0, 'd:\\EDAI\\OceanFront\\backend')

from services.query_executor import query_executor

queries = [
    "SELECT COUNT(*) as cnt FROM buoy_data",
    "SELECT * FROM buoy_data LIMIT 1",
    "SELECT platform_number, temp FROM buoy_data LIMIT 1",
    "SELECT platform_number, temp FROM buoy_data WHERE temp IS NOT NULL LIMIT 1",
]

print("=" * 60)
print("TESTING SIMPLE QUERIES")
print("=" * 60)

for sql in queries:
    print(f"\nSQL: {sql}")
    result = query_executor.execute(sql)
    print(f"  Success: {result['success']}, Rows: {result['row_count']}, Error: {result.get('error', 'None')}")
    if result['success'] and result['data']:
        print(f"  First row: {result['data'][0]}")
