"""
Result Formatter - Convert query results to beautiful Markdown
"""

from typing import List, Dict, Any

class ResultFormatter:
    """Format oceanographic query results as Markdown"""
    
    @staticmethod
    def format_as_markdown(data: List[Dict[str, Any]], query_info: Dict[str, str]) -> str:
        """
        Format query results as Markdown with tables, emojis, and structure
        
        Args:
            data: Query result rows as list of dicts
            query_info: Dict with 'explanation' and 'table' keys
        
        Returns:
            Markdown formatted string
        """
        
        if not data:
            return "❌ No data found for your query. Try a different search criteria."
        
        markdown = []
        
        # Header section
        markdown.append("## 🌊 Ocean Data Query Results")
        markdown.append("")
        
        # Only include description if it's meaningful (not auto-generated)
        explanation = query_info.get('explanation', '')
        if explanation and 'Generated query based on keywords' not in explanation:
            markdown.append(f"**Description:** {explanation}")
            markdown.append("")
        
        # Summary statistics
        markdown.append(f"📊 **Results:** {len(data)} records found")
        markdown.append("")
        
        # Data table
        if len(data) > 0:
            columns = list(data[0].keys())
            
            # Create markdown table header
            markdown.append("| " + " | ".join(columns) + " |")
            markdown.append("|" + "|".join(["---"] * len(columns)) + "|")
            
            # Add rows
            for row in data[:100]:  # Limit to 100 rows for readability
                values = []
                for col in columns:
                    val = row.get(col, "N/A")
                    
                    # Decode bytes to string
                    if isinstance(val, bytes):
                        val = val.decode('utf-8', errors='ignore').strip()
                    # Format values based on type
                    elif isinstance(val, float):
                        val = f"{val:.2f}"
                    elif val is None:
                        val = "N/A"
                    else:
                        val = str(val).strip()
                    
                    values.append(val)
                
                markdown.append("| " + " | ".join(values) + " |")
        
        markdown.append("")
        
        # Footer with metadata
        markdown.append("---")
        markdown.append(f"*Data source: OceanFront Database • {len(data)} records • Generated with Groq LLM*")
        
        return "\n".join(markdown)
    
    @staticmethod
    def format_error_response(error: str, query: str = "") -> str:
        """Format error as Markdown"""
        markdown = [
            "## ⚠️ Query Error",
            "",
            f"**Error:** {error}",
        ]
        
        if query:
            markdown.append("")
            markdown.append("**Your Query:**")
            markdown.append(f"```\n{query}\n```")
        
        markdown.append("")
        markdown.append("💡 **Suggestions:**")
        markdown.append("- Try asking about specific buoys (e.g., 'Show me IMBA-01 data')")
        markdown.append("- Ask about buoy locations (e.g., 'Which buoys are on the west coast?')")
        markdown.append("- Request data summaries (e.g., 'Average temperature in the Arabian Sea')")
        
        return "\n".join(markdown)
    
    @staticmethod
    def format_sql_with_explanation(sql: str, explanation: str, table: str) -> str:
        """Format SQL query with explanation (for debugging)"""
        markdown = [
            "## 📝 Query Details",
            "",
            f"**What it does:** {explanation}",
            f"**Data source:** {table}",
            "",
            "**SQL Query:**",
            f"```sql\n{sql}\n```",
        ]
        
        return "\n".join(markdown)


# Singleton instance
result_formatter = ResultFormatter()
