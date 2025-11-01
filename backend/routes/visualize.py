"""
Visualization routes for AgriSense 2.0
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import logging
import pandas as pd

logger = logging.getLogger(__name__)

router = APIRouter()


class VisualizationRequest(BaseModel):
    """Visualization request model"""
    query: str = Field(..., description="Query describing what to visualize")
    dataset_name: Optional[str] = Field(None, description="Specific dataset to use")
    chart_type: Optional[str] = Field(None, description="Force specific chart type: line, bar, scatter, map, table")
    filters: Optional[Dict[str, Any]] = Field(None, description="Data filters")
    limit: Optional[int] = Field(100, description="Maximum rows to visualize")


class VisualizationResponse(BaseModel):
    """Visualization response model"""
    chart_type: str
    chart_data: Dict[str, Any]
    data_summary: Dict[str, Any]
    message: str


@router.post("/visualize", response_model=VisualizationResponse)
async def create_visualization(request: VisualizationRequest):
    """
    Create visualization based on query and data
    
    Args:
        request: Visualization request
        
    Returns:
        Visualization response with chart data
    """
    from main import state
    
    if not state.initialized or not state.chart_builder:
        raise HTTPException(
            status_code=503,
            detail="Visualization service not ready"
        )
    
    try:
        logger.info(f"Creating visualization for: {request.query[:100]}...")
        
        # Get data
        if request.dataset_name and state.data_fusion:
            # Query specific dataset
            df = state.data_fusion.query_dataset(
                dataset_name=request.dataset_name,
                filters=request.filters,
                limit=request.limit
            )
        else:
            # Create sample data for demonstration
            # In production, this would query the actual datasets
            df = pd.DataFrame({
                'year': [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022],
                'rainfall_mm': [980, 1050, 890, 1100, 950, 1020, 980, 1150],
                'yield_kg_per_ha': [2720, 2800, 2600, 2900, 2680, 2750, 2720, 2850]
            })
        
        if df.empty:
            raise HTTPException(
                status_code=404,
                detail="No data available for visualization"
            )
        
        # Create visualization
        if request.chart_type:
            # Force specific chart type
            if request.chart_type == "line":
                viz_result = state.chart_builder.create_line_chart(
                    df, df.columns[0], df.columns[1], request.query
                )
            elif request.chart_type == "bar":
                viz_result = state.chart_builder.create_bar_chart(
                    df, df.columns[0], df.columns[1], request.query
                )
            elif request.chart_type == "scatter":
                viz_result = state.chart_builder.create_scatter_plot(
                    df, df.columns[0], df.columns[1], request.query
                )
            elif request.chart_type == "table":
                viz_result = state.chart_builder.create_table(df, request.query)
            else:
                viz_result = state.chart_builder.auto_visualize(request.query, df)
        else:
            # Auto-detect chart type
            viz_result = state.chart_builder.auto_visualize(request.query, df)
        
        # Data summary
        data_summary = {
            'rows': len(df),
            'columns': list(df.columns),
            'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
            'sample_data': df.head(5).to_dict(orient='records')
        }
        
        return VisualizationResponse(
            chart_type=viz_result.get('type', 'unknown'),
            chart_data=viz_result.get('data', {}),
            data_summary=data_summary,
            message=viz_result.get('message', 'Visualization created')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating visualization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class CorrelationRequest(BaseModel):
    """Request for correlation analysis"""
    dataset1: str
    dataset2: str
    value_col1: str
    value_col2: str
    merge_on: List[str]


@router.post("/correlate")
async def analyze_correlation(request: CorrelationRequest):
    """
    Analyze correlation between two datasets
    
    Args:
        request: Correlation request
        
    Returns:
        Correlation coefficient and visualization
    """
    from main import state
    
    if not state.data_fusion:
        raise HTTPException(status_code=503, detail="Data fusion service not ready")
    
    try:
        logger.info(f"Analyzing correlation between {request.dataset1} and {request.dataset2}")
        
        # Calculate correlation
        correlation, merged_df = state.data_fusion.calculate_correlation(
            dataset1_name=request.dataset1,
            dataset2_name=request.dataset2,
            value_col1=request.value_col1,
            value_col2=request.value_col2,
            merge_on=request.merge_on
        )
        
        if merged_df.empty:
            raise HTTPException(
                status_code=404,
                detail="Could not merge datasets or no common data found"
            )
        
        # Create scatter plot
        chart_data = {}
        if state.chart_builder:
            col1 = request.value_col1 if request.value_col1 in merged_df.columns else f"{request.value_col1}_left"
            col2 = request.value_col2 if request.value_col2 in merged_df.columns else f"{request.value_col2}_right"
            
            chart_data = state.chart_builder.create_scatter_plot(
                merged_df,
                col1,
                col2,
                f"Correlation: {request.value_col1} vs {request.value_col2}"
            )
        
        return {
            "correlation": correlation,
            "interpretation": "strong" if abs(correlation) > 0.7 else "moderate" if abs(correlation) > 0.4 else "weak",
            "direction": "positive" if correlation > 0 else "negative",
            "data_points": len(merged_df),
            "visualization": chart_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing correlation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class TimeSeriesRequest(BaseModel):
    """Request for time series analysis"""
    dataset_name: str
    time_column: str
    value_column: str
    group_by: Optional[str] = None


@router.post("/timeseries")
async def analyze_timeseries(request: TimeSeriesRequest):
    """
    Analyze time series data
    
    Args:
        request: Time series request
        
    Returns:
        Time series analysis and visualization
    """
    from main import state
    
    if not state.data_fusion:
        raise HTTPException(status_code=503, detail="Data fusion service not ready")
    
    try:
        logger.info(f"Analyzing time series for {request.dataset_name}")
        
        # Perform analysis
        analysis = state.data_fusion.time_series_analysis(
            dataset_name=request.dataset_name,
            time_column=request.time_column,
            value_column=request.value_column,
            group_by=request.group_by
        )
        
        if not analysis:
            raise HTTPException(
                status_code=404,
                detail="Could not analyze time series data"
            )
        
        # Create visualization
        chart_data = {}
        if state.chart_builder:
            df = state.data_fusion.query_dataset(request.dataset_name)
            chart_data = state.chart_builder.create_line_chart(
                df,
                request.time_column,
                request.value_column,
                f"Time Series: {request.value_column}",
                group_by=request.group_by
            )
        
        return {
            "analysis": analysis,
            "visualization": chart_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing time series: {e}")
        raise HTTPException(status_code=500, detail=str(e))
