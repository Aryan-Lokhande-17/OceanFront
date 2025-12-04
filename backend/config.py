import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Backend configuration"""
    
    # API Settings
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    _default_path = os.getenv("PARQUET_DATA_PATH", "../oceanFrontData/Parquet")
    PARQUET_DATA_PATH = Path(_default_path).resolve() if os.path.isabs(_default_path) else Path(__file__).parent.parent / _default_path
    PORT = int(os.getenv("PORT", 8000))
    HOST = os.getenv("HOST", "0.0.0.0")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./oceanfront.db")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Model settings
    LLM_MODEL = "openai/gpt-oss-120b"  # Groq model
    
    # Parquet schema definition for oceanographic data
    OCEAN_DATA_SCHEMA = {
        "buoy_data": {
            "columns": [
                "buoy_id", "buoy_name", "latitude", "longitude", "timestamp",
                "sst", "salinity", "wind_speed", "wind_direction", 
                "wave_height", "wave_period", "pressure", "current_speed"
            ],
            "description": "Real-time oceanographic buoy measurements from IMBA and NOAA NDBC"
        },
        "location_info": {
            "columns": [
                "buoy_id", "buoy_name", "coast", "latitude", "longitude", 
                "depth_m", "operator", "data_portal"
            ],
            "description": "Metadata about buoy locations and operators"
        }
    }

config = Config()
