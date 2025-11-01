"""
Sample data generation for AgriSense 2.0
Can be used independently or imported by other scripts
"""
import pandas as pd
import numpy as np
from pathlib import Path


def generate_rainfall_data(years=range(2015, 2023), states=None):
    """
    Generate sample rainfall data
    
    Args:
        years: Range of years to generate
        states: List of states (default: Tamil Nadu, Karnataka, Punjab)
        
    Returns:
        DataFrame with rainfall data
    """
    if states is None:
        states = ['Tamil Nadu', 'Karnataka', 'Punjab', 'Maharashtra', 'Uttar Pradesh']
    
    data = []
    base_rainfall = {
        'Tamil Nadu': 980,
        'Karnataka': 1150,
        'Punjab': 620,
        'Maharashtra': 1200,
        'Uttar Pradesh': 800
    }
    
    for state in states:
        base = base_rainfall.get(state, 1000)
        for year in years:
            # Add some variation
            rainfall = base + np.random.normal(0, 100)
            data.append({
                'state': state,
                'year': year,
                'rainfall_mm': round(rainfall, 2),
                'season': 'Annual'
            })
    
    return pd.DataFrame(data)


def generate_crop_production_data(years=range(2015, 2023), states=None):
    """
    Generate sample crop production data
    
    Args:
        years: Range of years to generate
        states: List of states
        
    Returns:
        DataFrame with crop production data
    """
    if states is None:
        states = ['Tamil Nadu', 'Karnataka', 'Punjab', 'Maharashtra', 'Uttar Pradesh']
    
    crops = ['Rice', 'Wheat', 'Sugarcane', 'Cotton', 'Maize']
    
    data = []
    base_production = {
        'Rice': 3000,
        'Wheat': 2800,
        'Sugarcane': 70000,
        'Cotton': 500,
        'Maize': 2500
    }
    
    base_yield = {
        'Rice': 2800,
        'Wheat': 3200,
        'Sugarcane': 70000,
        'Cotton': 400,
        'Maize': 2600
    }
    
    for state in states:
        # Each state grows 2-3 main crops
        state_crops = np.random.choice(crops, size=min(3, len(crops)), replace=False)
        
        for crop in state_crops:
            for year in years:
                production = base_production[crop] + np.random.normal(0, 200)
                area = production / base_yield[crop] * 1000
                yield_val = (production * 1000) / area if area > 0 else base_yield[crop]
                
                data.append({
                    'state': state,
                    'district': f"{state} District",
                    'year': year,
                    'season': 'Kharif',
                    'crop': crop,
                    'area_hectares': round(area, 2),
                    'production_tonnes': round(production, 2),
                    'yield_kg_per_ha': round(yield_val, 2)
                })
    
    return pd.DataFrame(data)


def generate_gdp_data(years=range(2015, 2023), states=None):
    """
    Generate sample agricultural GDP data
    
    Args:
        years: Range of years to generate
        states: List of states
        
    Returns:
        DataFrame with GDP data
    """
    if states is None:
        states = ['Tamil Nadu', 'Karnataka', 'Punjab', 'Maharashtra', 'Uttar Pradesh']
    
    data = []
    base_gdp = {
        'Tamil Nadu': 500000,
        'Karnataka': 450000,
        'Punjab': 350000,
        'Maharashtra': 600000,
        'Uttar Pradesh': 550000
    }
    
    for state in states:
        base = base_gdp.get(state, 400000)
        for year in years:
            total_gdp = base * (1.05 ** (year - 2015))  # 5% growth per year
            agri_gdp = total_gdp * np.random.uniform(0.15, 0.25)
            
            data.append({
                'state': state,
                'year': year,
                'gdp_agriculture': round(agri_gdp, 2),
                'total_gdp': round(total_gdp, 2),
                'agriculture_percentage': round((agri_gdp / total_gdp) * 100, 2)
            })
    
    return pd.DataFrame(data)


def save_all_datasets(output_dir='../data'):
    """
    Generate and save all sample datasets
    
    Args:
        output_dir: Directory to save CSV files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("Generating sample datasets...")
    
    # Generate datasets
    rainfall = generate_rainfall_data()
    crops = generate_crop_production_data()
    gdp = generate_gdp_data()
    
    # Save to CSV
    rainfall.to_csv(output_path / 'rainfall.csv', index=False)
    print(f"✓ Saved rainfall data: {len(rainfall)} records")
    
    crops.to_csv(output_path / 'crop_production.csv', index=False)
    print(f"✓ Saved crop production data: {len(crops)} records")
    
    gdp.to_csv(output_path / 'agricultural_gdp.csv', index=False)
    print(f"✓ Saved GDP data: {len(gdp)} records")
    
    print(f"\nAll datasets saved to {output_path}/")
    
    return rainfall, crops, gdp


if __name__ == "__main__":
    save_all_datasets()
