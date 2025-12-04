#!/usr/bin/env python
"""Test final fix for all query types"""

import requests

url = "http://localhost:8000/api/query"
queries = [
    "How does the monsoon affect ocean conditions?",
    "How many buoys are there?",
    "What data is available from the Indian Ocean Argo buoys?",
]

print("=" * 80)
print("FINAL TEST - EACH QUERY SHOULD RETURN RELEVANT DATA")
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
            print(f"\n📝 SQL Generated:\n{result.get('sql_query')[:150]}...")
            print(f"\n📋 Description:\n{result.get('sql_explanation')}")
            
            if result.get('success'):
                markdown = result.get('markdown_result', '')
                # Extract table data
                lines = markdown.split('\n')
                for line in lines:
                    if '|' in line:
                        print(line)
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
