"""
Data fusion layer - combine and query multiple datasets
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import logging
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


class DataFusion:
    """
    Combines and queries data from multiple sources
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize data fusion engine
        
        Args:
            database_url: Optional database connection string
        """
        self.datasets = {}  # In-memory cache of datasets
        self.metadata = {}  # Metadata about each dataset
        
        # Database connection
        if database_url:
            try:
                self.engine = create_engine(database_url)
                self.Session = sessionmaker(bind=self.engine)
                logger.info("Database connection established")
            except Exception as e:
                logger.warning(f"Could not connect to database: {e}")
                self.engine = None
                self.Session = None
        else:
            self.engine = None
            self.Session = None
    
    def register_dataset(
        self,
        name: str,
        df: pd.DataFrame,
        description: str = "",
        key_columns: Optional[List[str]] = None,
        time_column: Optional[str] = None
    ):
        """
        Register a dataset for fusion
        
        Args:
            name: Dataset name
            df: DataFrame
            description: Dataset description
            key_columns: Columns that can be used for joining
            time_column: Column representing time
        """
        self.datasets[name] = df
        self.metadata[name] = {
            'description': description,
            'columns': df.columns.tolist(),
            'key_columns': key_columns or [],
            'time_column': time_column,
            'shape': df.shape,
            'dtypes': df.dtypes.to_dict()
        }
        
        logger.info(f"Registered dataset '{name}' with {len(df)} rows")
    
    def get_dataset(self, name: str) -> Optional[pd.DataFrame]:
        """Get a registered dataset"""
        return self.datasets.get(name)
    
    def list_datasets(self) -> List[Dict[str, Any]]:
        """List all registered datasets with metadata"""
        return [
            {'name': name, **meta}
            for name, meta in self.metadata.items()
        ]
    
    def find_common_columns(self, dataset1: str, dataset2: str) -> List[str]:
        """
        Find common columns between two datasets
        
        Args:
            dataset1: First dataset name
            dataset2: Second dataset name
            
        Returns:
            List of common column names
        """
        if dataset1 not in self.datasets or dataset2 not in self.datasets:
            return []
        
        cols1 = set(self.datasets[dataset1].columns)
        cols2 = set(self.datasets[dataset2].columns)
        
        return list(cols1.intersection(cols2))
    
    def merge_datasets(
        self,
        left_name: str,
        right_name: str,
        on: Optional[List[str]] = None,
        how: str = 'inner'
    ) -> pd.DataFrame:
        """
        Merge two datasets
        
        Args:
            left_name: Name of left dataset
            right_name: Name of right dataset
            on: Columns to merge on (auto-detected if None)
            how: Merge type ('inner', 'outer', 'left', 'right')
            
        Returns:
            Merged DataFrame
        """
        if left_name not in self.datasets or right_name not in self.datasets:
            logger.error(f"One or both datasets not found: {left_name}, {right_name}")
            return pd.DataFrame()
        
        left_df = self.datasets[left_name]
        right_df = self.datasets[right_name]
        
        # Auto-detect merge columns
        if on is None:
            on = self.find_common_columns(left_name, right_name)
            if not on:
                logger.error(f"No common columns found between {left_name} and {right_name}")
                return pd.DataFrame()
        
        try:
            merged = pd.merge(left_df, right_df, on=on, how=how, suffixes=('_left', '_right'))
            logger.info(f"Merged {left_name} and {right_name} on {on}, resulting in {len(merged)} rows")
            return merged
        except Exception as e:
            logger.error(f"Error merging datasets: {e}")
            return pd.DataFrame()
    
    def query_dataset(
        self,
        dataset_name: str,
        filters: Optional[Dict[str, Any]] = None,
        columns: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Query a dataset with filters
        
        Args:
            dataset_name: Name of dataset
            filters: Dictionary of column:value filters
            columns: Columns to return (all if None)
            limit: Maximum rows to return
            
        Returns:
            Filtered DataFrame
        """
        if dataset_name not in self.datasets:
            logger.error(f"Dataset not found: {dataset_name}")
            return pd.DataFrame()
        
        df = self.datasets[dataset_name].copy()
        
        # Apply filters
        if filters:
            for col, value in filters.items():
                if col in df.columns:
                    if isinstance(value, (list, tuple)):
                        df = df[df[col].isin(value)]
                    else:
                        df = df[df[col] == value]
        
        # Select columns
        if columns:
            available_cols = [col for col in columns if col in df.columns]
            if available_cols:
                df = df[available_cols]
        
        # Apply limit
        if limit:
            df = df.head(limit)
        
        return df
    
    def aggregate_data(
        self,
        dataset_name: str,
        group_by: List[str],
        agg_funcs: Dict[str, str],
        filters: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Aggregate dataset
        
        Args:
            dataset_name: Name of dataset
            group_by: Columns to group by
            agg_funcs: Dictionary of column:aggregation_function
            filters: Optional filters to apply before aggregation
            
        Returns:
            Aggregated DataFrame
        """
        df = self.query_dataset(dataset_name, filters)
        
        if df.empty:
            return df
        
        try:
            # Ensure group_by columns exist
            valid_group_cols = [col for col in group_by if col in df.columns]
            
            if not valid_group_cols:
                logger.error(f"No valid group_by columns found in {dataset_name}")
                return pd.DataFrame()
            
            # Aggregate
            result = df.groupby(valid_group_cols).agg(agg_funcs).reset_index()
            logger.info(f"Aggregated {dataset_name} by {valid_group_cols}")
            return result
            
        except Exception as e:
            logger.error(f"Error aggregating dataset: {e}")
            return pd.DataFrame()
    
    def calculate_correlation(
        self,
        dataset1_name: str,
        dataset2_name: str,
        value_col1: str,
        value_col2: str,
        merge_on: List[str]
    ) -> Tuple[float, pd.DataFrame]:
        """
        Calculate correlation between two datasets
        
        Args:
            dataset1_name: First dataset
            dataset2_name: Second dataset
            value_col1: Column from first dataset
            value_col2: Column from second dataset
            merge_on: Columns to merge on
            
        Returns:
            Tuple of (correlation coefficient, merged DataFrame)
        """
        # Merge datasets
        merged = self.merge_datasets(dataset1_name, dataset2_name, on=merge_on)
        
        if merged.empty:
            return 0.0, pd.DataFrame()
        
        # Calculate correlation
        try:
            # Handle suffixes
            col1 = value_col1 if value_col1 in merged.columns else f"{value_col1}_left"
            col2 = value_col2 if value_col2 in merged.columns else f"{value_col2}_right"
            
            # Drop NaN values
            merged_clean = merged[[col1, col2]].dropna()
            
            if len(merged_clean) < 2:
                return 0.0, merged
            
            correlation = merged_clean[col1].corr(merged_clean[col2])
            logger.info(f"Correlation between {value_col1} and {value_col2}: {correlation:.3f}")
            
            return float(correlation), merged
            
        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return 0.0, merged
    
    def time_series_analysis(
        self,
        dataset_name: str,
        time_column: str,
        value_column: str,
        group_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze time series data
        
        Args:
            dataset_name: Name of dataset
            time_column: Column representing time
            value_column: Column with values
            group_by: Optional column to group by
            
        Returns:
            Dictionary with analysis results
        """
        df = self.query_dataset(dataset_name)
        
        if df.empty:
            return {}
        
        try:
            # Ensure time column is datetime
            if not pd.api.types.is_datetime64_any_dtype(df[time_column]):
                df[time_column] = pd.to_datetime(df[time_column], errors='coerce')
            
            # Sort by time
            df = df.sort_values(time_column)
            
            results = {
                'dataset': dataset_name,
                'time_range': {
                    'start': str(df[time_column].min()),
                    'end': str(df[time_column].max())
                },
                'data_points': len(df)
            }
            
            if group_by and group_by in df.columns:
                # Group analysis
                groups = {}
                for group_name, group_df in df.groupby(group_by):
                    values = group_df[value_column].dropna()
                    groups[str(group_name)] = {
                        'mean': float(values.mean()),
                        'std': float(values.std()),
                        'min': float(values.min()),
                        'max': float(values.max()),
                        'trend': 'increasing' if values.iloc[-1] > values.iloc[0] else 'decreasing'
                    }
                results['groups'] = groups
            else:
                # Overall analysis
                values = df[value_column].dropna()
                results['statistics'] = {
                    'mean': float(values.mean()),
                    'std': float(values.std()),
                    'min': float(values.min()),
                    'max': float(values.max()),
                    'trend': 'increasing' if values.iloc[-1] > values.iloc[0] else 'decreasing'
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Error in time series analysis: {e}")
            return {}
    
    def execute_sql(self, query: str) -> pd.DataFrame:
        """
        Execute SQL query on database
        
        Args:
            query: SQL query string
            
        Returns:
            Query results as DataFrame
        """
        if not self.engine:
            logger.error("No database connection available")
            return pd.DataFrame()
        
        try:
            df = pd.read_sql(text(query), self.engine)
            logger.info(f"Executed SQL query, returned {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Error executing SQL: {e}")
            return pd.DataFrame()
