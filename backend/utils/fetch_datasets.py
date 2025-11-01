"""
Data fetching utilities for data.gov.in APIs
"""
import requests
import pandas as pd
import json
from typing import Dict, List, Optional, Union
from pathlib import Path
import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class DataGovFetcher:
    """Fetch and process data from data.gov.in APIs"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.data.gov.in/resource"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        
    def fetch_dataset(self, resource_id: str, filters: Optional[Dict] = None, 
                      limit: int = 1000, offset: int = 0) -> pd.DataFrame:
        """
        Fetch a dataset from data.gov.in
        
        Args:
            resource_id: The unique identifier for the dataset
            filters: Optional filters to apply
            limit: Number of records to fetch
            offset: Starting offset for pagination
            
        Returns:
            DataFrame with the fetched data
        """
        try:
            params = {
                "api-key": self.api_key,
                "format": "json",
                "limit": limit,
                "offset": offset
            }
            
            if filters:
                params["filters"] = json.dumps(filters)
            
            url = f"{self.base_url}/{resource_id}"
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if "records" in data:
                df = pd.DataFrame(data["records"])
                logger.info(f"Fetched {len(df)} records from {resource_id}")
                return df
            else:
                logger.warning(f"No records found in response from {resource_id}")
                return pd.DataFrame()
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching dataset {resource_id}: {e}")
            return pd.DataFrame()
    
    def fetch_paginated(self, resource_id: str, filters: Optional[Dict] = None,
                       max_records: int = 10000) -> pd.DataFrame:
        """
        Fetch dataset with automatic pagination
        
        Args:
            resource_id: The unique identifier for the dataset
            filters: Optional filters to apply
            max_records: Maximum number of records to fetch
            
        Returns:
            DataFrame with all fetched data
        """
        all_data = []
        offset = 0
        batch_size = 1000
        
        while offset < max_records:
            df = self.fetch_dataset(resource_id, filters, batch_size, offset)
            
            if df.empty:
                break
                
            all_data.append(df)
            
            if len(df) < batch_size:
                break
                
            offset += batch_size
            time.sleep(0.5)  # Rate limiting
        
        if all_data:
            result = pd.concat(all_data, ignore_index=True)
            logger.info(f"Fetched total of {len(result)} records from {resource_id}")
            return result
        else:
            return pd.DataFrame()
    
    def fetch_csv(self, url: str) -> pd.DataFrame:
        """
        Fetch CSV file directly from URL
        
        Args:
            url: Direct URL to CSV file
            
        Returns:
            DataFrame with CSV data
        """
        try:
            df = pd.read_csv(url)
            logger.info(f"Successfully loaded CSV from {url}")
            return df
        except Exception as e:
            logger.error(f"Error loading CSV from {url}: {e}")
            return pd.DataFrame()
    
    def fetch_excel(self, url: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch Excel file from URL
        
        Args:
            url: Direct URL to Excel file
            sheet_name: Optional sheet name to load
            
        Returns:
            DataFrame with Excel data
        """
        try:
            df = pd.read_excel(url, sheet_name=sheet_name)
            logger.info(f"Successfully loaded Excel from {url}")
            return df
        except Exception as e:
            logger.error(f"Error loading Excel from {url}: {e}")
            return pd.DataFrame()
    
    def save_dataset(self, df: pd.DataFrame, filename: str, data_dir: Path) -> bool:
        """
        Save dataset to local storage
        
        Args:
            df: DataFrame to save
            filename: Name for the saved file
            data_dir: Directory to save to
            
        Returns:
            True if successful
        """
        try:
            filepath = data_dir / filename
            
            if filename.endswith('.csv'):
                df.to_csv(filepath, index=False)
            elif filename.endswith('.parquet'):
                df.to_parquet(filepath, index=False)
            elif filename.endswith('.json'):
                df.to_json(filepath, orient='records', indent=2)
            else:
                df.to_csv(filepath, index=False)
            
            logger.info(f"Saved dataset to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving dataset to {filename}: {e}")
            return False


# Predefined dataset configurations for common agricultural datasets
AGRICULTURAL_DATASETS = {
    "rainfall": {
        "description": "IMD Rainfall Data",
        "resource_ids": [
            "9ef84268-d588-465a-a308-a864a43d0070",  # Example ID
        ],
        "fields": ["state", "district", "year", "month", "rainfall_mm"]
    },
    "crop_production": {
        "description": "Agricultural Crop Production Statistics",
        "resource_ids": [
            "c3baa01d-3baf-47e3-a658-a95da09f9ddf",  # Example ID
        ],
        "fields": ["state", "district", "year", "season", "crop", "area", "production", "yield"]
    },
    "agri_gdp": {
        "description": "Agricultural GDP Contribution",
        "resource_ids": [
            "agriculture-gdp-india",  # Example ID
        ],
        "fields": ["year", "state", "gdp_agriculture", "total_gdp", "percentage"]
    }
}


def normalize_dataset(df: pd.DataFrame, dataset_type: str) -> pd.DataFrame:
    """
    Normalize column names and formats for consistent processing
    
    Args:
        df: Input DataFrame
        dataset_type: Type of dataset (rainfall, crop_production, etc.)
        
    Returns:
        Normalized DataFrame
    """
    # Create a copy
    df = df.copy()
    
    # Common normalizations
    # Convert column names to lowercase and replace spaces with underscores
    df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')
    
    # Type-specific normalizations
    if dataset_type == "rainfall":
        # Ensure numeric columns
        if 'rainfall_mm' in df.columns:
            df['rainfall_mm'] = pd.to_numeric(df['rainfall_mm'], errors='coerce')
        if 'year' in df.columns:
            df['year'] = pd.to_numeric(df['year'], errors='coerce')
            
    elif dataset_type == "crop_production":
        # Standardize crop names
        if 'crop' in df.columns:
            df['crop'] = df['crop'].str.title().str.strip()
        # Ensure numeric columns
        numeric_cols = ['area', 'production', 'yield', 'year']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Remove rows with all NaN values
    df = df.dropna(how='all')
    
    return df
