#!/usr/bin/env python
"""Test SQL generation"""

import sys
sys.path.insert(0, 'd:\\EDAI\\OceanFront\\backend')

from services.nl_to_sql import nl_converter

query = "What temperature measurements do we have?"

print("=" * 60)
print("TESTING SQL GENERATION")
print("=" * 60)
print(f"\nQuery: {query}")

result = nl_converter.convert(query)

print(f"\nSuccess: {result['success']}")
print(f"SQL: {result['sql']}")
print(f"Explanation: {result['explanation']}")
