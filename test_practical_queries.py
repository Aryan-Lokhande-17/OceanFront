#!/usr/bin/env python
"""Test practical queries that should work"""

import requests

url = "http://localhost:8000/api/query"
queries = [
    "Show me temperature and salinity for each buoy",
    "What is the average temperature for each buoy?",
    "Show me all measurements from buoy 1901514",
    "Which buoy has the highest temperature?",
    "Show me latitude and longitude for each buoy",
]

print("=" * 70)
print("TESTING PRACTICAL QUERIES")
print("=" * 70)

for i, query in enumerate(queries, 1):
    print(f"\n\n{'='*70}")
    print(f"Query {i}: {query}")
    print('='*70)
    
    try:
        response = requests.post(url, json={"query": query, "include_sql": True})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('success')}")
            print(f"Row count: {result.get('row_count')}")
            
            if result.get('sql_query'):
                print(f"\nSQL: {result.get('sql_query')[:100]}...")
            
            if result.get('success'):
                markdown = result.get('markdown_result', '')
                # Show first 400 chars
                print(f"\nResult (first 400 chars):\n{markdown[:400]}")
            else:
                print(f"Error: {result.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
