#!/usr/bin/env python
"""Test multiple queries"""

import requests

url = "http://localhost:8000/api/query"
queries = [
    "What temperature measurements do we have?",
    "Show me salinity data",
    "How many unique buoys do we have?",
]

print("=" * 60)
print("TESTING MULTIPLE QUERIES")
print("=" * 60)

for query in queries:
    print(f"\n\nQuery: {query}")
    print("-" * 60)
    
    try:
        response = requests.post(url, json={"query": query, "include_sql": False})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('success')}")
            print(f"Row count: {result.get('row_count')}")
            
            if result.get('success'):
                markdown = result.get('markdown_result', '')
                # Show first 500 chars
                print(f"\nResult (first 500 chars):\n{markdown[:500]}")
            else:
                print(f"Error: {result.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
