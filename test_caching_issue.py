#!/usr/bin/env python
"""Test for caching issues"""

import requests

url = "http://localhost:8000/api/query"
queries = [
    "How many argo buoys are there?",
    "How does the monsoon affect ocean conditions?",
    "What depth measurements are available?",
]

print("=" * 80)
print("TESTING FOR CACHING ISSUES - EACH QUERY SHOULD GENERATE DIFFERENT SQL")
print("=" * 80)

for i, query in enumerate(queries, 1):
    print(f"\n\n{'='*80}")
    print(f"Query {i}: {query}")
    print('='*80)
    
    try:
        response = requests.post(url, json={"query": query, "include_sql": True})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('success')}")
            print(f"Row count: {result.get('row_count')}")
            print(f"\n📝 SQL Generated:\n{result.get('sql_query')}")
            print(f"\n📋 Description:\n{result.get('sql_explanation')}")
            
            if result.get('success'):
                markdown = result.get('markdown_result', '')
                # Show first 300 chars
                print(f"\n📊 Result (first 300 chars):\n{markdown[:300]}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
