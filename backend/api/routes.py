"""FastAPI routes for data queries and chat"""

from fastapi import APIRouter, HTTPException
from models.schemas import QueryRequest, QueryResponse, ChatRequest
from services import nl_converter, query_executor, result_formatter
from services.query_classifier import QueryClassifier
from services.ml_predictor import ml_predictor
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/query", response_model=QueryResponse)
async def execute_data_query(request: QueryRequest) -> QueryResponse:
    """
    Execute a natural language query on oceanographic data
    
    Flow:
    1. Convert NL query to SQL using Groq
    2. Execute SQL on Parquet files using DuckDB
    3. Format results as Markdown
    
    Args:
        request: QueryRequest with 'query' field
    
    Returns:
        QueryResponse with markdown formatted results
    """
    
    try:
        logger.info(f"📝 Processing query: {request.query}")
        
        # Step 0: Classify query intent
        query_intent = QueryClassifier.classify(request.query)
        logger.info(f"Query intent: {query_intent}")
        
        # Handle explanation queries
        if query_intent == 'explanation':
            explanation = QueryClassifier.get_explanation_response(request.query)
            return QueryResponse(
                success=True,
                markdown_result=explanation,
                sql_query=None,
                sql_explanation=None,
                row_count=0,
                error=None
            )
        
        # Handle descriptive queries
        elif query_intent == 'descriptive':
            description = QueryClassifier.get_descriptive_response(request.query)
            return QueryResponse(
                success=True,
                markdown_result=description,
                sql_query=None,
                sql_explanation=None,
                row_count=0,
                error=None
            )
        
        # Step 1: NL → SQL Conversion (for data queries)
        print("\n🔄 STEP 1: Converting Natural Language to SQL...")
        sql_result = nl_converter.convert(request.query)
        
        if not sql_result['success']:
            logger.error(f"SQL conversion failed: {sql_result.get('explanation')}")
            markdown = result_formatter.format_error_response(
                sql_result.get('explanation', 'Failed to convert query to SQL'),
                request.query
            )
            return QueryResponse(
                success=False,
                markdown_result=markdown,
                sql_query=None,
                sql_explanation=None,
                row_count=0,
                error=sql_result.get('explanation')
            )
        
        sql_query = sql_result.get('sql')
        sql_explanation = sql_result.get('explanation')
        table = sql_result.get('table')
        confidence = sql_result.get('confidence', 0.5)
        
        print(f"✅ SQL Generated (confidence: {confidence:.1%}):")
        print(f"   {sql_query}")
        print(f"   Explanation: {sql_explanation}")
        
        # Step 2: Execute SQL Query
        print("\n🔄 STEP 2: Executing SQL Query on Parquet Data...")
        execution_result = query_executor.execute(sql_query)
        
        if not execution_result['success']:
            logger.error(f"Query execution failed: {execution_result.get('error')}")
            markdown = result_formatter.format_error_response(
                execution_result.get('error', 'Query execution failed'),
                sql_query
            )
            return QueryResponse(
                success=False,
                markdown_result=markdown,
                sql_query=sql_query if request.include_sql else None,
                sql_explanation=sql_explanation if request.include_sql else None,
                row_count=0,
                error=execution_result.get('error')
            )
        
        data = execution_result['data']
        row_count = execution_result['row_count']
        
        print(f"✅ Query executed successfully")
        print(f"   Rows returned: {row_count}")
        
        # Step 3: Format Results as Markdown
        print("\n🔄 STEP 3: Formatting Results as Markdown...")
        markdown_result = result_formatter.format_as_markdown(
            data,
            {'explanation': sql_explanation, 'table': table}
        )
        
        print(f"✅ Results formatted")
        
        return QueryResponse(
            success=True,
            markdown_result=markdown_result,
            sql_query=sql_query if request.include_sql else None,
            sql_explanation=sql_explanation if request.include_sql else None,
            row_count=row_count,
            error=None
        )
    
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        markdown = result_formatter.format_error_response(f"Unexpected error: {str(e)}")
        return QueryResponse(
            success=False,
            markdown_result=markdown,
            sql_query=None,
            sql_explanation=None,
            row_count=0,
            error=str(e)
        )


@router.post("/chat")
async def chat_with_data(request: ChatRequest):
    """
    Chat endpoint that can use data queries
    
    If use_data_queries=True, tries to fetch real data
    Otherwise just returns chat response
    """
    
    try:
        last_message = request.messages[-1]
        
        if request.use_data_queries:
            # Try to execute as data query
            query_request = QueryRequest(
                query=last_message.content,
                include_sql=False
            )
            result = await execute_data_query(query_request)
            
            return {
                "success": result.success,
                "response": result.markdown_result,
                "type": "data_query" if result.success else "chat",
                "row_count": result.row_count
            }
        else:
            # Just return chat response (handled by frontend's Groq integration)
            return {
                "success": True,
                "response": "Use the Groq chat endpoint for general queries",
                "type": "chat",
                "row_count": 0
            }
    
    except Exception as e:
        logger.exception(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "nl_converter": "ready",
            "query_executor": "ready",
            "result_formatter": "ready",
            "ml_predictor": "ready"
        }
    }


@router.post("/predict")
async def get_ml_predictions(latitude: float, longitude: float, temperature: float = None, salinity: float = None):
    """
    Get ML model predictions for a location
    
    Uses LSTM, RandomForest, and XGBoost models to predict:
    - Temperature profiles
    - Salinity anomalies
    - Mixed layer depth
    
    Args:
        latitude: Latitude
        longitude: Longitude
        temperature: Optional water temperature
        salinity: Optional salinity
    
    Returns:
        dict with predictions from all models
    """
    try:
        buoy_data = {
            "latitude": latitude,
            "longitude": longitude,
            "temperature": temperature or 25.0,
            "salinity": salinity or 35.0
        }
        
        predictions = ml_predictor.get_prediction_summary(buoy_data)
        
        # Format as markdown
        markdown = f"""
# ML Model Predictions

**Location:** {latitude:.2f}°N, {longitude:.2f}°E

## Temperature Profile Prediction
- Model: LSTM Neural Network
- Status: {'Available' if predictions['models']['temperature_profile']['success'] else 'Not available'}

## Salinity Anomaly
- Predicted Salinity: {predictions['models']['salinity_anomaly'].get('predicted_salinity', 'N/A')} PSU
- Based on Temperature: {predictions['models']['salinity_anomaly'].get('temperature', 'N/A')}°C

## Mixed Layer Depth (MLD)
- Predicted MLD: {predictions['models']['mixed_layer_depth'].get('predicted_mld_meters', 'N/A')} meters
- Regional: {'Bay of Bengal' if longitude > 85 else 'Arabian Sea' if longitude < 72 else 'Indian Ocean'}

---
*Predictions generated using machine learning models trained on historical oceanographic data*
        """
        
        return {
            "success": True,
            "predictions": predictions,
            "markdown_result": markdown
        }
    except Exception as e:
        logger.exception(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
