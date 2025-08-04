from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class SurveyResponse(Base):
    __tablename__ = "survey_responses"
    
    id = Column(Integer, primary_key=True)
    survey_id = Column(String, unique=True, index=True)
    customer_id = Column(String, index=True)
    customer_name = Column(String)
    response_text = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    tier = Column(String)
    
    # LLM extracted fields
    sentiment = Column(String)
    features_mentioned = Column(Text)  # JSON string
    issues = Column(Text)  # JSON string
    competitors_mentioned = Column(Text)  # JSON string
    revenue_impact = Column(Boolean, default=False)
    
class Flag(Base):
    __tablename__ = "flags"
    
    id = Column(Integer, primary_key=True)
    survey_id = Column(String, index=True)
    customer_name = Column(String)
    tier = Column(String)
    flag_score = Column(Float)
    flag_reasons = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db(engine):
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)