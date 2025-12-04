#!/usr/bin/env python
"""Test the query endpoint"""

import requests
import json

url = "http://localhost:8000/api/query"
query = "What temperature measurements do we have?"

payload = {
    "query": query,
    "include_sql": True
}

print("=" * 60)
print("TESTING QUERY ENDPOINT")
print("=" * 60)
print(f"\nQuery: {query}")

try:
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Success: {result.get('success')}")
        print(f"Row count: {result.get('row_count')}")
        
        if result.get('success'):
            print(f"\nMarkdown Result (first 1000 chars):\n{result.get('markdown_result')[:1000]}")
        else:
            print(f"\nError: {result.get('error')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Connection error: {e}")
