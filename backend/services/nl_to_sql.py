"""
NL-to-SQL Converter using Groq LLM
Converts natural language queries to DuckDB SQL queries
"""

from groq import Groq
from config import config
import json
import re

class NLToSQLConverter:
    """Convert Natural Language queries to SQL using Groq LLM"""
    
    def __init__(self):
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = config.LLM_MODEL
        self.schema_context = self._build_schema_context()
    
    def _generate_fallback_query(self, query: str) -> str:
        """Generate a basic query based on keywords when LLM fails"""
        query_lower = query.lower()
        
        # HIGHEST PRIORITY: Check for count/aggregate queries FIRST
        if any(word in query_lower for word in ['how many', 'count', 'total', 'number of']):
            if 'buoy' in query_lower or 'platform' in query_lower:
                return "SELECT COUNT(DISTINCT CAST(platform_number AS VARCHAR)) as unique_buoys, COUNT(*) as total_measurements FROM buoy_data"
            elif 'temperature' in query_lower or 'temp' in query_lower:
                return "SELECT COUNT(*) as temperature_records FROM buoy_data WHERE temp IS NOT NULL"
            elif 'salinity' in query_lower or 'psal' in query_lower:
                return "SELECT COUNT(*) as salinity_records FROM buoy_data WHERE psal IS NOT NULL"
            elif 'depth' in query_lower or 'pressure' in query_lower or 'pres' in query_lower:
                return "SELECT COUNT(*) as depth_records FROM buoy_data WHERE pres IS NOT NULL"
            else:
                return "SELECT COUNT(*) as total_records, COUNT(DISTINCT CAST(platform_number AS VARCHAR)) as unique_buoys FROM buoy_data"
        
        # Check for trend/pattern/seasonal queries (BEFORE location checks)
        elif any(word in query_lower for word in ['trend', 'pattern', 'seasonal', 'monsoon', 'variation', 'change', 'affect']):
            if 'temperature' in query_lower or 'temp' in query_lower:
                return "SELECT DISTINCT CAST(platform_number AS VARCHAR) as platform, ROUND(CAST(temp AS FLOAT), 2) as temperature FROM buoy_data WHERE temp IS NOT NULL ORDER BY platform_number, temp LIMIT 100"
            elif 'salinity' in query_lower or 'psal' in query_lower:
                return "SELECT DISTINCT CAST(platform_number AS VARCHAR) as platform, ROUND(CAST(psal AS FLOAT), 2) as salinity FROM buoy_data WHERE psal IS NOT NULL ORDER BY platform_number, psal LIMIT 100"
            else:
                # Return all measurements for trend analysis
                return "SELECT DISTINCT CAST(platform_number AS VARCHAR) as platform, ROUND(CAST(temp AS FLOAT), 2) as temperature, ROUND(CAST(psal AS FLOAT), 2) as salinity, ROUND(CAST(pres AS FLOAT), 2) as depth FROM buoy_data ORDER BY platform_number LIMIT 100"
        
        # Check for specific location queries (EXACT MATCH for Indian Ocean)
        elif 'indian ocean' in query_lower or 'arabian sea' in query_lower or 'bay of bengal' in query_lower:
            return "SELECT DISTINCT CAST(platform_number AS VARCHAR) as platform, CAST(latitude AS FLOAT) as latitude, CAST(longitude AS FLOAT) as longitude, ROUND(CAST(temp AS FLOAT), 2) as temperature, ROUND(CAST(psal AS FLOAT), 2) as salinity, ROUND(CAST(pres AS FLOAT), 2) as depth FROM buoy_data WHERE latitude BETWEEN -40 AND 30 AND longitude BETWEEN 20 AND 120 LIMIT 100"
        
        # Check for depth-only queries
        elif any(word in query_lower for word in ['depth', 'pressure', 'pres', 'deep']) and 'temperature' not in query_lower and 'salinity' not in query_lower:
            return "SELECT DISTINCT CAST(platform_number AS VARCHAR) as platform, ROUND(CAST(pres AS FLOAT), 2) as depth FROM buoy_data WHERE pres IS NOT NULL ORDER BY platform_number LIMIT 100"
        
        # Check for salinity-only queries
        elif any(word in query_lower for word in ['salinity', 'salt', 'psal']) and 'temperature' not in query_lower:
            return "SELECT DISTINCT CAST(platform_number AS VARCHAR) as platform, ROUND(CAST(psal AS FLOAT), 2) as salinity FROM buoy_data WHERE psal IS NOT NULL ORDER BY platform_number LIMIT 100"
        
        # Check for temperature-related queries
        elif any(word in query_lower for word in ['temperature', 'temp', 'warm', 'heat', 'thermal']):
            return "SELECT DISTINCT CAST(platform_number AS VARCHAR) as platform, ROUND(CAST(temp AS FLOAT), 2) as temperature FROM buoy_data WHERE temp IS NOT NULL ORDER BY platform_number LIMIT 100"
        
        # Check for location queries
        elif any(word in query_lower for word in ['location', 'latitude', 'longitude', 'region', 'where', 'position']):
            return "SELECT DISTINCT CAST(platform_number AS VARCHAR) as platform, CAST(latitude AS FLOAT) as latitude, CAST(longitude AS FLOAT) as longitude FROM buoy_data LIMIT 100"
        
        # Check for comparison/aggregate queries
        elif any(word in query_lower for word in ['average', 'mean', 'max', 'min', 'compare', 'highest', 'lowest']):
            if 'temperature' in query_lower or 'temp' in query_lower:
                return "SELECT CAST(platform_number AS VARCHAR) as platform, ROUND(AVG(CAST(temp AS FLOAT)), 2) as avg_temperature, ROUND(MAX(CAST(temp AS FLOAT)), 2) as max_temperature, ROUND(MIN(CAST(temp AS FLOAT)), 2) as min_temperature FROM buoy_data WHERE temp IS NOT NULL GROUP BY platform_number LIMIT 100"
            elif 'salinity' in query_lower or 'psal' in query_lower:
                return "SELECT CAST(platform_number AS VARCHAR) as platform, ROUND(AVG(CAST(psal AS FLOAT)), 2) as avg_salinity FROM buoy_data WHERE psal IS NOT NULL GROUP BY platform_number LIMIT 100"
            elif 'depth' in query_lower or 'pressure' in query_lower:
                return "SELECT CAST(platform_number AS VARCHAR) as platform, ROUND(AVG(CAST(pres AS FLOAT)), 2) as avg_depth FROM buoy_data WHERE pres IS NOT NULL GROUP BY platform_number LIMIT 100"
            else:
                return "SELECT COUNT(*) as total_records, COUNT(DISTINCT CAST(platform_number AS VARCHAR)) as unique_buoys FROM buoy_data"
        
        # Default: return temperature + salinity + depth (comprehensive view)
        else:
            return "SELECT DISTINCT CAST(platform_number AS VARCHAR) as platform, ROUND(CAST(temp AS FLOAT), 2) as temperature, ROUND(CAST(psal AS FLOAT), 2) as salinity, ROUND(CAST(pres AS FLOAT), 2) as depth FROM buoy_data LIMIT 100"
    
    def _build_schema_context(self) -> str:
        """Build schema information for the LLM prompt"""
        schema_info = """
        DATABASE SCHEMA - REAL ARGO PROFILE DATA (ALL COLUMNS FROM PARQUET FILES):
        
        PRIMARY TABLE: buoy_data (RAW Argo float profiles - ALL 68+ columns from NetCDF)
        Key columns include:
           - platform_number: Argo float ID
           - latitude, longitude: Position of profile
           - juld, juld_location: Profile timestamp
           - temp, temp_adjusted: Temperature (°C) at various depths
           - psal, psal_adjusted: Salinity (PSU) at various depths  
           - pres, pres_adjusted: Pressure (dbar) / depth
           - cycle_number: Profile cycle number
           - data_mode, data_state_indicator: Data quality flags
           - And 50+ more technical columns...
        
        SUMMARY TABLE: location_info (for regional queries)
           - buoy_id: Platform number
           - latitude, longitude: Profile position
           - temperature: Water temperature
           - salinity: Water salinity
           - pressure: Water pressure/depth
           - region: 'Indian Ocean', 'Arabian Sea', 'Bay of Bengal'
           - operator: 'Argo Program'
        
        DATA VOLUME:
        - Multiple Parquet files covering different profiles
        - Each file contains multiple depth levels per profile
        - Total records: Hundreds to thousands of measurements
        
        CRITICAL RULES FOR SQL GENERATION:
        1. USE buoy_data TABLE for all queries (has all raw measurements)
        2. Include LIMIT 100 to avoid huge result sets
        3. Use IS NOT NULL filters for optional columns
        4. Use DISTINCT to deduplicate similar records
        5. Use CAST() to handle mixed types: CAST(column AS FLOAT/VARCHAR) for proper formatting
        6. Temperature is in column 'temp', depth/pressure in 'pres'
        7. Salinity is in column 'psal'
        8. Location is in columns: latitude, longitude, platform_number
        9. Use CAST(platform_number AS VARCHAR) to ensure string format (not bytes)
        10. Use ROUND(CAST(x AS FLOAT), 2) for numeric values
        
        QUERY INTERPRETATION GUIDE:
        - "Show me X for each buoy" → SELECT DISTINCT platform_number, X columns GROUP BY or ORDER BY platform_number
        - "What data is available from [location]" → SELECT columns WHERE latitude/longitude match the location
        - "How does [phenomenon] affect" → SELECT relevant columns that show the effect/correlation
        - "Average/Min/Max of X" → Use aggregate functions: AVG(), MIN(), MAX()
        - "Unique/Count of X" → Use COUNT(DISTINCT X)
        - "Top/Bottom X" → Use ORDER BY ... LIMIT N
        - "Trends/Patterns in X" → SELECT platform_number, X columns ORDER BY platform_number to show variations
        - "X in [region]" → SELECT columns WHERE latitude/longitude are in that region
        - "Compare X between" → SELECT platform_number, X columns to allow comparison
        
        KEYWORD MAPPING (use these to identify what user wants):
        - Temperature keywords: "temp", "temperature", "warm", "heat", "thermal"
        - Salinity keywords: "salinity", "salt", "psal"
        - Depth/Pressure keywords: "depth", "pressure", "pres", "deep"
        - Location keywords: "Arabian Sea", "Bay of Bengal", "Indian Ocean", "latitude", "longitude", "region"
        - Trend keywords: "trend", "pattern", "seasonal", "variation", "change", "compare"
        - Aggregate keywords: "average", "mean", "max", "min", "total", "count"
        
        IMPORTANT: NO FILTERING BY COLUMN NAME - just query what's available!
        
        EXAMPLE QUERIES (ALL USE buoy_data WITH DISTINCT and CAST):
        - "Temperature data" → SELECT DISTINCT CAST(platform_number AS VARCHAR) as platform, ROUND(CAST(temp AS FLOAT), 2) as temp, ROUND(CAST(pres AS FLOAT), 2) as pressure FROM buoy_data WHERE temp IS NOT NULL LIMIT 100
        - "Show salinity" → SELECT DISTINCT CAST(platform_number AS VARCHAR) as platform, ROUND(CAST(psal AS FLOAT), 2) as salinity FROM buoy_data WHERE psal IS NOT NULL LIMIT 100
        - "Depth measurements" → SELECT DISTINCT CAST(platform_number AS VARCHAR) as platform, ROUND(CAST(pres AS FLOAT), 2) as depth FROM buoy_data WHERE pres IS NOT NULL LIMIT 100
        - "All profiles" → SELECT DISTINCT CAST(platform_number AS VARCHAR) as platform, CAST(latitude AS FLOAT) as lat, CAST(longitude AS FLOAT) as lon FROM buoy_data LIMIT 100
        - "Regional data" → SELECT DISTINCT CAST(platform_number AS VARCHAR) as platform, CAST(latitude AS FLOAT) as latitude, CAST(longitude AS FLOAT) as longitude FROM buoy_data WHERE latitude > 10 LIMIT 100
        - "Count measurements" → SELECT COUNT(DISTINCT CAST(platform_number AS VARCHAR)) as unique_platforms, COUNT(*) as total_measurements FROM buoy_data
        - "Pressure profiles" → SELECT DISTINCT CAST(platform_number AS VARCHAR) as platform, ROUND(CAST(pres AS FLOAT), 2) as pressure FROM buoy_data ORDER BY platform LIMIT 100
        - "Temperature and salinity for each buoy" → SELECT DISTINCT CAST(platform_number AS VARCHAR) as platform, ROUND(CAST(temp AS FLOAT), 2) as temperature, ROUND(CAST(psal AS FLOAT), 2) as salinity FROM buoy_data WHERE temp IS NOT NULL AND psal IS NOT NULL ORDER BY platform LIMIT 100
        - "Average temperature by buoy" → SELECT CAST(platform_number AS VARCHAR) as platform, ROUND(AVG(CAST(temp AS FLOAT)), 2) as avg_temperature FROM buoy_data WHERE temp IS NOT NULL GROUP BY platform_number LIMIT 100
        - "Buoys in specific region" → SELECT DISTINCT CAST(platform_number AS VARCHAR) as platform, CAST(latitude AS FLOAT) as latitude, CAST(longitude AS FLOAT) as longitude, ROUND(CAST(temp AS FLOAT), 2) as temperature FROM buoy_data WHERE latitude BETWEEN 0 AND 30 AND longitude BETWEEN 40 AND 80 LIMIT 100
        - "Temperature trends" → SELECT DISTINCT CAST(platform_number AS VARCHAR) as platform, ROUND(CAST(temp AS FLOAT), 2) as temperature, CAST(latitude AS FLOAT) as latitude, CAST(longitude AS FLOAT) as longitude FROM buoy_data WHERE temp IS NOT NULL ORDER BY platform_number, temp LIMIT 100
        - "Temperature in Arabian Sea" → SELECT DISTINCT CAST(platform_number AS VARCHAR) as platform, ROUND(CAST(temp AS FLOAT), 2) as temperature, CAST(latitude AS FLOAT) as latitude, CAST(longitude AS FLOAT) as longitude FROM buoy_data WHERE temp IS NOT NULL AND latitude BETWEEN 0 AND 25 AND longitude BETWEEN 40 AND 80 LIMIT 100
        - "Seasonal patterns" → SELECT DISTINCT CAST(platform_number AS VARCHAR) as platform, ROUND(CAST(temp AS FLOAT), 2) as temperature, ROUND(CAST(psal AS FLOAT), 2) as salinity FROM buoy_data WHERE temp IS NOT NULL ORDER BY platform_number LIMIT 100
        """
        return schema_info
    
    def convert(self, natural_language_query: str) -> dict:
        """
        Convert NL query to SQL query using Groq
        
        Args:
            natural_language_query: User's natural language question
        
        Returns:
            dict with keys:
                - sql: Generated SQL query
                - explanation: What the query does
                - table: Which table(s) are queried
        """
        
        system_prompt = f"""You are a SQL expert that converts natural language questions to DuckDB SQL queries.

{self.schema_context}

RULES:
1. Only generate valid DuckDB SQL
2. Use standard SQL syntax (SELECT, WHERE, JOIN, etc.)
3. Always include column names clearly
4. Use LIMIT 100 to avoid huge result sets
5. Return ONLY the SQL query, no explanations (unless asked in "explanation" field)
6. Handle date/time queries with CAST or DATE functions
7. Use ILIKE for case-insensitive matching
8. Always specify which table(s) you're querying

Respond in JSON format:
{{
    "sql": "SELECT ... FROM ...",
    "explanation": "What this query does",
    "table": "table_name or 'multi-table'",
    "confidence": 0.0-1.0
}}"""
        
        user_message = f"Convert this question to SQL: {natural_language_query}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.3  # Lower temperature for more deterministic SQL
            )
            
            response_text = response.choices[0].message.content
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "sql": result.get("sql", ""),
                    "explanation": result.get("explanation", ""),
                    "table": result.get("table", ""),
                    "confidence": result.get("confidence", 0.5),
                    "success": True
                }
            else:
                # Fallback: Try to generate a basic query based on keywords
                fallback_sql = self._generate_fallback_query(natural_language_query)
                if fallback_sql:
                    return {
                        "sql": fallback_sql,
                        "explanation": "Generated query based on keywords in your question",
                        "table": "buoy_data",
                        "confidence": 0.3,
                        "success": True
                    }
                
                return {
                    "sql": "",
                    "explanation": "Could not understand your query. Try asking about: temperature, salinity, depth, location, or specific buoys.",
                    "table": "",
                    "confidence": 0,
                    "success": False,
                    "raw_response": response_text
                }
        
        except Exception as e:
            return {
                "sql": "",
                "explanation": f"Error converting query: {str(e)}",
                "table": "",
                "confidence": 0,
                "success": False,
                "error": str(e)
            }


# Singleton instance
nl_converter = NLToSQLConverter()
