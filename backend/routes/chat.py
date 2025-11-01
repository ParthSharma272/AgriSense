"""
Chat routes for AgriSense 2.0
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model"""
    query: str = Field(..., description="User's question")
    include_reasoning: bool = Field(True, description="Include reasoning chain in response")
    include_visualization: bool = Field(True, description="Include automatic visualization")
    policy_mode: bool = Field(False, description="Enable policy insight mode")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional data filters")


class ChatResponse(BaseModel):
    """Chat response model"""
    query: str
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    visualization: Optional[Dict[str, Any]] = None
    policy_insights: Optional[str] = None
    reasoning_chain: Optional[str] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - answer questions using RAG pipeline
    
    Args:
        request: Chat request with query and options
        
    Returns:
        Chat response with answer, sources, and optional visualization
    """
    from main import state
    
    if not state.initialized or not state.rag_pipeline:
        raise HTTPException(
            status_code=503,
            detail="AgriSense is still initializing. Please try again in a moment."
        )
    
    try:
        logger.info(f"Processing query: {request.query[:100]}...")
        
        # Query RAG pipeline
        rag_result = state.rag_pipeline.rag_query(
            query=request.query,
            include_reasoning=request.include_reasoning
        )
        
        response = ChatResponse(
            query=request.query,
            answer=rag_result['answer'],
            sources=rag_result.get('sources', []),
            confidence=rag_result.get('confidence', 0.0)
        )
        
        # Add visualization if requested and data is available
        if request.include_visualization and state.chart_builder:
            try:
                # Try to extract data for visualization from sources
                # This is a simplified version - you'd extract actual data
                visualization = {
                    "type": "info",
                    "message": "Visualization data will be available after dataset integration"
                }
                response.visualization = visualization
            except Exception as e:
                logger.warning(f"Error creating visualization: {e}")
        
        # Add policy insights if requested
        if request.policy_mode:
            try:
                policy_prompt = f"Based on this analysis: {rag_result['answer']}\n\nProvide data-driven policy recommendations for Indian agriculture:"
                
                policy_insights = state.rag_pipeline.generate_response(
                    query=policy_prompt,
                    context=rag_result.get('context', ''),
                    include_reasoning=False,
                    max_tokens=512
                )
                
                response.policy_insights = policy_insights
            except Exception as e:
                logger.warning(f"Error generating policy insights: {e}")
        
        # Add reasoning chain if available
        if request.include_reasoning:
            response.reasoning_chain = rag_result.get('context', '')
        
        logger.info(f"Query processed successfully with confidence {response.confidence:.2f}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class IndexRequest(BaseModel):
    """Request to index new data"""
    dataset_name: str
    resource_id: Optional[str] = None
    csv_url: Optional[str] = None
    description: str = ""


@router.post("/index")
async def index_data(request: IndexRequest, background_tasks: BackgroundTasks):
    """
    Index new data into the RAG system
    
    Args:
        request: Index request with dataset information
        background_tasks: FastAPI background tasks
        
    Returns:
        Status message
    """
    from main import state
    import pandas as pd
    
    if not state.initialized:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        logger.info(f"Indexing dataset: {request.dataset_name}")
        
        # Fetch data
        df = pd.DataFrame()
        
        if request.resource_id and state.data_fetcher:
            df = state.data_fetcher.fetch_paginated(request.resource_id)
        elif request.csv_url and state.data_fetcher:
            df = state.data_fetcher.fetch_csv(request.csv_url)
        else:
            raise HTTPException(
                status_code=400,
                detail="Must provide either resource_id or csv_url"
            )
        
        if df.empty:
            raise HTTPException(
                status_code=404,
                detail="Could not fetch data or data is empty"
            )
        
        # Register with data fusion
        if state.data_fusion:
            state.data_fusion.register_dataset(
                name=request.dataset_name,
                df=df,
                description=request.description
            )
        
        # Index in RAG pipeline (async in background)
        if state.rag_pipeline:
            def index_in_background():
                # Convert DataFrame to text documents
                documents = []
                metadatas = []
                
                for idx, row in df.iterrows():
                    doc_text = " | ".join([f"{col}: {row[col]}" for col in df.columns])
                    documents.append(doc_text)
                    metadatas.append({
                        "dataset": request.dataset_name,
                        "row_id": str(idx),
                        "description": request.description
                    })
                
                state.rag_pipeline.add_documents(
                    documents=documents,
                    metadatas=metadatas,
                    collection_name="gov_datasets"
                )
                
                logger.info(f"Indexed {len(documents)} documents from {request.dataset_name}")
            
            background_tasks.add_task(index_in_background)
        
        return {
            "status": "success",
            "message": f"Indexing {len(df)} records from {request.dataset_name}",
            "dataset_name": request.dataset_name,
            "rows": len(df),
            "columns": list(df.columns)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error indexing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets")
async def list_datasets():
    """
    List all registered datasets
    
    Returns:
        List of datasets with metadata
    """
    from main import state
    
    if not state.data_fusion:
        return {"datasets": []}
    
    try:
        datasets = state.data_fusion.list_datasets()
        return {"datasets": datasets}
    except Exception as e:
        logger.error(f"Error listing datasets: {e}")
        raise HTTPException(status_code=500, detail=str(e))
