"""
Initialization script for AgriSense 2.0
Downloads sample data and sets up the RAG pipeline
"""
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from models.database import init_database
from models.llm_rag import RAGPipeline
from models.datafusion import DataFusion
from utils.fetch_datasets import DataGovFetcher, normalize_dataset
import pandas as pd
from sqlalchemy import create_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_database():
    """Initialize database schema"""
    logger.info("Initializing database...")
    try:
        engine = create_engine(settings.DATABASE_URL)
        init_database(engine)
        logger.info("✓ Database initialized")
        return True
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        return False


def create_sample_data():
    """Create sample datasets for testing"""
    logger.info("Creating sample data...")
    
    # Sample rainfall data
    rainfall_df = pd.DataFrame({
        'state': ['Tamil Nadu'] * 8 + ['Karnataka'] * 8,
        'year': list(range(2015, 2023)) * 2,
        'rainfall_mm': [980, 1050, 890, 1100, 950, 1020, 980, 1150,
                       1150, 1200, 1080, 1250, 1100, 1180, 1150, 1300]
    })
    
    # Sample crop production data
    crop_df = pd.DataFrame({
        'state': ['Tamil Nadu'] * 8 + ['Karnataka'] * 8,
        'year': list(range(2015, 2023)) * 2,
        'crop': ['Rice'] * 16,
        'production_tonnes': [7200, 7500, 7000, 7800, 7100, 7400, 7200, 7900,
                             9100, 9500, 9000, 9800, 9200, 9600, 9100, 10000],
        'area_hectares': [2650, 2680, 2690, 2690, 2650, 2690, 2650, 2770,
                         2980, 3120, 2950, 3200, 3080, 3140, 3080, 3500],
        'yield_kg_per_ha': [2720, 2800, 2600, 2900, 2680, 2750, 2720, 2850,
                           3050, 3045, 3050, 3063, 2987, 3057, 2955, 2857]
    })
    
    # Save to data directory
    rainfall_df.to_csv(settings.DATA_DIR / 'rainfall.csv', index=False)
    crop_df.to_csv(settings.DATA_DIR / 'crop_production.csv', index=False)
    
    logger.info("✓ Sample data created")
    return rainfall_df, crop_df


def initialize_rag_pipeline(rainfall_df, crop_df):
    """Initialize RAG pipeline with sample data"""
    logger.info("Initializing RAG pipeline...")
    
    if not settings.HF_API_TOKEN:
        logger.warning("✗ HF_API_TOKEN not set. RAG pipeline cannot be initialized.")
        logger.warning("  Please set HF_API_TOKEN in .env file")
        return False
    
    try:
        rag = RAGPipeline(
            hf_token=settings.HF_API_TOKEN,
            hf_model=settings.HF_MODEL,
            embedding_model=settings.EMBEDDING_MODEL,
            chroma_persist_dir=settings.CHROMA_PERSIST_DIR
        )
        
        # Create collection
        rag.create_collection("gov_datasets", recreate=True)
        
        # Index rainfall data
        rainfall_docs = []
        rainfall_meta = []
        for _, row in rainfall_df.iterrows():
            doc = f"In {row['year']}, {row['state']} received {row['rainfall_mm']}mm of rainfall."
            rainfall_docs.append(doc)
            rainfall_meta.append({
                'dataset': 'rainfall',
                'state': row['state'],
                'year': str(row['year'])
            })
        
        rag.add_documents(rainfall_docs, rainfall_meta, "gov_datasets")
        logger.info(f"✓ Indexed {len(rainfall_docs)} rainfall records")
        
        # Index crop production data
        crop_docs = []
        crop_meta = []
        for _, row in crop_df.iterrows():
            doc = f"In {row['year']}, {row['state']} produced {row['production_tonnes']} tonnes of {row['crop']} with a yield of {row['yield_kg_per_ha']} kg/ha."
            crop_docs.append(doc)
            crop_meta.append({
                'dataset': 'crop_production',
                'state': row['state'],
                'year': str(row['year']),
                'crop': row['crop']
            })
        
        rag.add_documents(crop_docs, crop_meta, "gov_datasets")
        logger.info(f"✓ Indexed {len(crop_docs)} crop production records")
        
        logger.info("✓ RAG pipeline initialized")
        return True
        
    except Exception as e:
        logger.error(f"✗ RAG pipeline initialization failed: {e}")
        return False


def main():
    """Main initialization routine"""
    print("=" * 60)
    print("AgriSense 2.0 Initialization")
    print("=" * 60)
    print()
    
    # Check environment
    logger.info("Checking environment...")
    if not settings.HF_API_TOKEN:
        logger.warning("⚠ HF_API_TOKEN not set")
        logger.warning("  Some features will be limited")
    
    if not settings.DATA_GOV_API_KEY:
        logger.warning("⚠ DATA_GOV_API_KEY not set")
        logger.warning("  Live data fetching will be limited")
    
    print()
    
    # Initialize database
    # db_success = initialize_database()
    # print()
    
    # Create sample data
    rainfall_df, crop_df = create_sample_data()
    print()
    
    # Initialize RAG pipeline
    rag_success = initialize_rag_pipeline(rainfall_df, crop_df)
    print()
    
    # Summary
    print("=" * 60)
    print("Initialization Summary")
    print("=" * 60)
    # print(f"Database: {'✓' if db_success else '✗'}")
    print(f"Sample Data: ✓")
    print(f"RAG Pipeline: {'✓' if rag_success else '✗'}")
    print()
    
    if rag_success:
        print("✓ AgriSense 2.0 is ready!")
        print()
        print("To start the backend:")
        print("  cd backend")
        print("  uvicorn main:app --reload")
        print()
        print("To start the frontend:")
        print("  cd frontend")
        print("  npm install")
        print("  npm run dev")
    else:
        print("⚠ Initialization completed with warnings")
        print("  Please check the logs above")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
