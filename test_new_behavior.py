#!/usr/bin/env python
"""Test new intelligent query behavior"""

import requests

url = "http://localhost:8000/api/query"
test_queries = [
    ("Explain the seasonal patterns in ocean temperature", "EXPLANATION"),
    ("What depth measurements are available?", "DATA"),
    ("What data is available from Indian Ocean Argo buoys?", "DESCRIPTIVE"),
    ("Show me temperature data", "DATA"),
    ("How does the monsoon affect ocean conditions?", "EXPLANATION"),
]

print("=" * 80)
print("TESTING NEW INTELLIGENT QUERY BEHAVIOR")
print("=" * 80)

for query, expected_type in test_queries:
    print(f"\n\n{'='*80}")
    print(f"Query: {query}")
    print(f"Expected Type: {expected_type}")
    print('='*80)
    
    try:
        response = requests.post(url, json={"query": query, "include_sql": False})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('success')}")
            
            markdown = result.get('markdown_result', '')
            
            # Show first 600 characters
            print(f"\n📝 Response (first 600 chars):\n{markdown[:600]}")
            
            # Check if it's the right type
            if expected_type == "EXPLANATION":
                if "##" in markdown and ("Monsoon" in markdown or "Temperature" in markdown or "Salinity" in markdown):
                    print("\n✅ Correctly returned EXPLANATION (scientific content)")
                else:
                    print("\n❌ Should have returned EXPLANATION")
            elif expected_type == "DATA":
                if "|" in markdown and "---" in markdown:
                    print("\n✅ Correctly returned DATA (table format)")
                else:
                    print("\n❌ Should have returned DATA (table)")
            elif expected_type == "DESCRIPTIVE":
                if "Available" in markdown or "Measurements" in markdown:
                    print("\n✅ Correctly returned DESCRIPTIVE (data description)")
                else:
                    print("\n❌ Should have returned DESCRIPTIVE")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
