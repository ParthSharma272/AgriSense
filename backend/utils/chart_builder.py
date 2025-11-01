"""
Chart and visualization generation utilities
"""
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Any, Tuple
import json
import logging
from pathlib import Path
import io
import base64

logger = logging.getLogger(__name__)


class ChartBuilder:
    """
    Automatic chart generation based on data and query type
    """
    
    def __init__(self, width: int = 800, height: int = 600):
        """
        Initialize chart builder
        
        Args:
            width: Default chart width
            height: Default chart height
        """
        self.width = width
        self.height = height
        self.default_theme = "plotly_dark"
    
    def detect_chart_type(self, query: str, df: pd.DataFrame) -> str:
        """
        Detect appropriate chart type based on query and data
        
        Args:
            query: User's query string
            df: DataFrame to visualize
            
        Returns:
            Chart type: 'line', 'bar', 'scatter', 'map', 'table'
        """
        query_lower = query.lower()
        
        # Time series detection
        if any(word in query_lower for word in ['trend', 'over time', 'years', 'temporal', 'timeline']):
            return 'line'
        
        # Comparison detection
        if any(word in query_lower for word in ['compare', 'comparison', 'versus', 'vs', 'between']):
            return 'bar'
        
        # Correlation detection
        if any(word in query_lower for word in ['correlation', 'relationship', 'affect', 'impact']):
            return 'scatter'
        
        # Geographic detection
        if any(word in query_lower for word in ['state', 'district', 'region', 'map', 'geography']):
            # Check if we have geographic data
            geo_columns = ['state', 'district', 'region', 'location']
            if any(col in df.columns for col in geo_columns):
                return 'map'
            return 'bar'
        
        # Default: check data shape
        if len(df) > 50:
            return 'line'
        else:
            return 'bar'
    
    def create_line_chart(
        self,
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str = "Trend Over Time",
        group_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a line chart
        
        Args:
            df: DataFrame
            x_col: Column for x-axis (usually time)
            y_col: Column for y-axis
            title: Chart title
            group_by: Optional column to group lines by
            
        Returns:
            Plotly chart as JSON
        """
        try:
            if group_by and group_by in df.columns:
                fig = px.line(
                    df,
                    x=x_col,
                    y=y_col,
                    color=group_by,
                    title=title,
                    template=self.default_theme
                )
            else:
                fig = px.line(
                    df,
                    x=x_col,
                    y=y_col,
                    title=title,
                    template=self.default_theme
                )
            
            fig.update_layout(
                width=self.width,
                height=self.height,
                hovermode='x unified'
            )
            
            return json.loads(fig.to_json())
            
        except Exception as e:
            logger.error(f"Error creating line chart: {e}")
            return {}
    
    def create_bar_chart(
        self,
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str = "Comparison",
        orientation: str = 'v',
        group_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a bar chart
        
        Args:
            df: DataFrame
            x_col: Column for x-axis
            y_col: Column for y-axis
            title: Chart title
            orientation: 'v' for vertical, 'h' for horizontal
            group_by: Optional column to group bars by
            
        Returns:
            Plotly chart as JSON
        """
        try:
            if group_by and group_by in df.columns:
                fig = px.bar(
                    df,
                    x=x_col,
                    y=y_col,
                    color=group_by,
                    title=title,
                    orientation=orientation,
                    template=self.default_theme,
                    barmode='group'
                )
            else:
                fig = px.bar(
                    df,
                    x=x_col,
                    y=y_col,
                    title=title,
                    orientation=orientation,
                    template=self.default_theme
                )
            
            fig.update_layout(
                width=self.width,
                height=self.height
            )
            
            return json.loads(fig.to_json())
            
        except Exception as e:
            logger.error(f"Error creating bar chart: {e}")
            return {}
    
    def create_scatter_plot(
        self,
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str = "Correlation Analysis",
        color_by: Optional[str] = None,
        size_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a scatter plot
        
        Args:
            df: DataFrame
            x_col: Column for x-axis
            y_col: Column for y-axis
            title: Chart title
            color_by: Optional column for point colors
            size_by: Optional column for point sizes
            
        Returns:
            Plotly chart as JSON
        """
        try:
            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                color=color_by,
                size=size_by,
                title=title,
                template=self.default_theme,
                trendline="ols"  # Add trend line
            )
            
            fig.update_layout(
                width=self.width,
                height=self.height
            )
            
            return json.loads(fig.to_json())
            
        except Exception as e:
            logger.error(f"Error creating scatter plot: {e}")
            return {}
    
    def create_choropleth_map(
        self,
        df: pd.DataFrame,
        location_col: str,
        value_col: str,
        title: str = "Geographic Distribution",
        location_type: str = "state"
    ) -> Dict[str, Any]:
        """
        Create a choropleth map for India
        
        Args:
            df: DataFrame
            location_col: Column with location names
            value_col: Column with values to visualize
            title: Chart title
            location_type: 'state' or 'district'
            
        Returns:
            Plotly chart as JSON
        """
        try:
            # For India, we use geojson-id mapping
            # This is a simplified version - you'd need actual geojson data
            fig = px.choropleth(
                df,
                locations=location_col,
                locationmode="geojson-id",
                color=value_col,
                title=title,
                template=self.default_theme,
                color_continuous_scale="Viridis"
            )
            
            # Focus on India
            fig.update_geos(
                fitbounds="locations",
                visible=False
            )
            
            fig.update_layout(
                width=self.width,
                height=self.height
            )
            
            return json.loads(fig.to_json())
            
        except Exception as e:
            logger.error(f"Error creating map: {e}")
            # Fallback to bar chart
            return self.create_bar_chart(df, location_col, value_col, title)
    
    def create_table(self, df: pd.DataFrame, title: str = "Data Table") -> Dict[str, Any]:
        """
        Create a formatted table
        
        Args:
            df: DataFrame to display
            title: Table title
            
        Returns:
            Table data as JSON
        """
        try:
            # Limit rows for display
            display_df = df.head(100)
            
            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=list(display_df.columns),
                    fill_color='darkslategray',
                    align='left',
                    font=dict(color='white', size=12)
                ),
                cells=dict(
                    values=[display_df[col] for col in display_df.columns],
                    fill_color='#1e1e1e',
                    align='left',
                    font=dict(color='white', size=11)
                )
            )])
            
            fig.update_layout(
                title=title,
                width=self.width,
                height=self.height,
                template=self.default_theme
            )
            
            return json.loads(fig.to_json())
            
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            return {}
    
    def auto_visualize(
        self,
        query: str,
        df: pd.DataFrame,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Automatically create appropriate visualization
        
        Args:
            query: User's query
            df: DataFrame to visualize
            title: Optional custom title
            
        Returns:
            Dictionary with chart type and chart data
        """
        if df.empty:
            return {'type': 'none', 'data': {}, 'message': 'No data to visualize'}
        
        # Detect chart type
        chart_type = self.detect_chart_type(query, df)
        
        # Generate title if not provided
        if not title:
            title = f"Analysis: {query[:50]}..."
        
        # Create appropriate chart
        chart_data = {}
        
        if chart_type == 'line':
            # Find time column
            time_cols = ['year', 'month', 'date', 'time', 'period']
            time_col = next((col for col in df.columns if col.lower() in time_cols), None)
            
            # Find numeric column
            numeric_cols = df.select_dtypes(include=['number']).columns
            value_col = numeric_cols[0] if len(numeric_cols) > 0 else df.columns[-1]
            
            if time_col:
                chart_data = self.create_line_chart(df, time_col, value_col, title)
            else:
                chart_data = self.create_bar_chart(df, df.columns[0], value_col, title)
        
        elif chart_type == 'bar':
            categorical_col = df.columns[0]
            numeric_cols = df.select_dtypes(include=['number']).columns
            value_col = numeric_cols[0] if len(numeric_cols) > 0 else df.columns[-1]
            
            chart_data = self.create_bar_chart(df, categorical_col, value_col, title)
        
        elif chart_type == 'scatter':
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) >= 2:
                chart_data = self.create_scatter_plot(
                    df, numeric_cols[0], numeric_cols[1], title
                )
            else:
                chart_data = self.create_table(df, title)
        
        elif chart_type == 'map':
            geo_cols = ['state', 'district', 'region']
            location_col = next((col for col in df.columns if col.lower() in geo_cols), None)
            numeric_cols = df.select_dtypes(include=['number']).columns
            value_col = numeric_cols[0] if len(numeric_cols) > 0 else df.columns[-1]
            
            if location_col:
                chart_data = self.create_choropleth_map(df, location_col, value_col, title)
            else:
                chart_data = self.create_bar_chart(df, df.columns[0], value_col, title)
        
        else:  # table
            chart_data = self.create_table(df, title)
        
        return {
            'type': chart_type,
            'data': chart_data,
            'message': f'Generated {chart_type} visualization'
        }


def detect_columns(df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Detect column types in a DataFrame
    
    Args:
        df: Input DataFrame
        
    Returns:
        Dictionary categorizing columns by type
    """
    return {
        'numeric': df.select_dtypes(include=['number']).columns.tolist(),
        'categorical': df.select_dtypes(include=['object', 'category']).columns.tolist(),
        'datetime': df.select_dtypes(include=['datetime']).columns.tolist(),
        'time_like': [col for col in df.columns if col.lower() in 
                     ['year', 'month', 'date', 'time', 'period', 'season']],
        'geographic': [col for col in df.columns if col.lower() in 
                      ['state', 'district', 'region', 'location', 'place', 'area']]
    }
