"""
OceanFront Backend - Main FastAPI Application

Pipeline Flow:
1. User sends NL query to /api/query endpoint
2. NL-to-SQL converter (Groq) converts question to SQL
3. Query executor (DuckDB) runs SQL on Parquet files
4. Result formatter converts output to Markdown
5. Response sent back to frontend
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from config import config

# Configure logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="OceanFront Backend",
    description="AI-powered oceanographic data query system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api", tags=["data"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "OceanFront Backend",
        "version": "1.0.0",
        "endpoints": {
            "query": "/api/query (POST) - Convert NL to SQL and execute",
            "chat": "/api/chat (POST) - Chat with data support",
            "health": "/api/health (GET) - Health check"
        },
        "pipeline": {
            "step_1": "Natural Language Query",
            "step_2": "NL-to-SQL Conversion (Groq LLM)",
            "step_3": "SQL Query Execution (DuckDB + Parquet)",
            "step_4": "Result Formatting (Markdown)",
            "step_5": "Response to Frontend"
        }
    }

@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    logger.info("🚀 OceanFront Backend Starting...")
    logger.info(f"📊 Data path: {config.PARQUET_DATA_PATH}")
    logger.info(f"🌐 Server: {config.HOST}:{config.PORT}")
    logger.info("✅ Backend ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown tasks"""
    logger.info("🛑 Backend shutting down...")

if __name__ == "__main__":
    import uvicorn
    
    print("""
    
    ╔════════════════════════════════════════╗
    ║     🌊 OceanFront Backend Starting     ║
    ╚════════════════════════════════════════╝
    
    Pipeline:
    User Query
      ↓
    NL-to-SQL Converter (Groq LLM)
      ↓
    Parquet Query Executor (DuckDB)
      ↓
    Result Formatter (Markdown)
      ↓
    Frontend Response
    
    """)
    
    uvicorn.run(
        app,
        host=config.HOST,
        port=config.PORT,
        log_level=config.LOG_LEVEL.lower()
    )
