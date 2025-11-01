"""
Database models and schema for AgriSense 2.0
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Dataset(Base):
    """Dataset metadata"""
    __tablename__ = 'datasets'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    source_url = Column(String(512))
    resource_id = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    row_count = Column(Integer)
    column_count = Column(Integer)
    schema_info = Column(JSON)
    
    # Relationships
    records = relationship("DataRecord", back_populates="dataset", cascade="all, delete-orphan")


class DataRecord(Base):
    """Individual data records"""
    __tablename__ = 'data_records'
    
    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey('datasets.id'), nullable=False)
    data = Column(JSON, nullable=False)
    indexed_text = Column(Text)  # For full-text search
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    dataset = relationship("Dataset", back_populates="records")


class RainfallData(Base):
    """Rainfall data - optimized for time-series queries"""
    __tablename__ = 'rainfall_data'
    
    id = Column(Integer, primary_key=True)
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), index=True)
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, index=True)
    rainfall_mm = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class CropProduction(Base):
    """Crop production data"""
    __tablename__ = 'crop_production'
    
    id = Column(Integer, primary_key=True)
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), index=True)
    year = Column(Integer, nullable=False, index=True)
    season = Column(String(50), index=True)
    crop = Column(String(100), nullable=False, index=True)
    area_hectares = Column(Float)
    production_tonnes = Column(Float)
    yield_kg_per_ha = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class AgriculturalGDP(Base):
    """Agricultural GDP data"""
    __tablename__ = 'agricultural_gdp'
    
    id = Column(Integer, primary_key=True)
    state = Column(String(100), index=True)
    year = Column(Integer, nullable=False, index=True)
    gdp_agriculture = Column(Float)
    total_gdp = Column(Float)
    agriculture_percentage = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class QueryLog(Base):
    """Log of user queries for analytics"""
    __tablename__ = 'query_logs'
    
    id = Column(Integer, primary_key=True)
    query_text = Column(Text, nullable=False)
    response_confidence = Column(Float)
    sources_used = Column(JSON)
    execution_time = Column(Float)
    policy_mode = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


# Database initialization function
def init_database(engine):
    """
    Initialize database schema
    
    Args:
        engine: SQLAlchemy engine
    """
    Base.metadata.create_all(engine)
    print("Database schema initialized successfully")


# Database session helper
from contextlib import contextmanager
from sqlalchemy.orm import Session


@contextmanager
def get_db_session(engine):
    """
    Context manager for database sessions
    
    Args:
        engine: SQLAlchemy engine
        
    Yields:
        Database session
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
