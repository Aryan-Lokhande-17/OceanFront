#!/usr/bin/env python
"""Test seasonal patterns query"""

import requests

url = "http://localhost:8000/api/query"
query = "Explain the seasonal patterns in ocean temperature"

print("=" * 70)
print("TESTING SEASONAL PATTERNS QUERY")
print("=" * 70)
print(f"\nQuery: {query}\n")

try:
    response = requests.post(url, json={"query": query, "include_sql": True})
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Row count: {result.get('row_count')}")
        print(f"\nSQL Generated:\n{result.get('sql_query')}")
        print(f"\nSQL Explanation:\n{result.get('sql_explanation')}")
        
        if result.get('success'):
            markdown = result.get('markdown_result', '')
            print(f"\n{'='*70}")
            print("FULL RESULT:")
            print('='*70)
            print(markdown)
        else:
            print(f"\n❌ Error: {result.get('error')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Connection error: {e}")
