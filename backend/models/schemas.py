"""Pydantic models for API validation"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    """Request model for data queries"""
    query: str  # Natural language query
    include_sql: bool = False  # Whether to include SQL in response


class QueryResponse(BaseModel):
    """Response model for data queries"""
    success: bool
    markdown_result: str  # Formatted markdown result
    sql_query: Optional[str] = None  # SQL if requested
    sql_explanation: Optional[str] = None
    row_count: int
    error: Optional[str] = None


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str  # 'user' or 'assistant'
    content: str


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    messages: List[ChatMessage]
    use_data_queries: bool = True  # Whether to use data queries or just chat


class BuoyDataRequest(BaseModel):
    """Request for specific buoy data"""
    buoy_id: Optional[str] = None
    buoy_name: Optional[str] = None
    time_range: Optional[Dict[str, str]] = None  # {'start': '2025-12-01', 'end': '2025-12-04'}
    fields: Optional[List[str]] = None  # Specific columns to retrieve
