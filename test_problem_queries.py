#!/usr/bin/env python
"""Test the problematic queries"""

import requests

url = "http://localhost:8000/api/query"
queries = [
    "Show me temperature and salinity for each buoy",
    "What data is available from the Indian Ocean Argo buoys?",
    "How does the monsoon affect ocean conditions?",
]

print("=" * 70)
print("TESTING PROBLEMATIC QUERIES - SHOULD NOW RETURN DIFFERENT RESULTS")
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
            print(f"\nSQL Generated:\n{result.get('sql_query')}")
            print(f"\nDescription: {result.get('sql_explanation')}")
            
            if result.get('success'):
                markdown = result.get('markdown_result', '')
                # Show first 600 chars
                print(f"\nResult:\n{markdown[:600]}")
            else:
                print(f"Error: {result.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
