"""
Database models for Phishing Email Detection System
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String(500))
    status = Column(String(50), default='pending')
    is_phishing = Column(Boolean)
    confidence_score = Column(Float)
    sender = Column(String(255))
    subject = Column(Text)
    body = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    iocs = relationship("IOC", back_populates="email", cascade="all, delete-orphan")
    analysis_logs = relationship("AnalysisLog", back_populates="email", cascade="all, delete-orphan")
    ml_predictions = relationship("MLPrediction", back_populates="email", cascade="all, delete-orphan")

class IOC(Base):
    __tablename__ = 'iocs'

    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey('emails.id', ondelete='CASCADE'))
    ioc_type = Column(String(50), nullable=False)
    ioc_value = Column(Text, nullable=False)
    severity = Column(String(20), default='low')
    detection_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    email = relationship("Email", back_populates="iocs")

class AnalysisLog(Base):
    __tablename__ = 'analysis_logs'

    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey('emails.id', ondelete='CASCADE'))
    analysis_start = Column(DateTime, default=datetime.utcnow)
    analysis_end = Column(DateTime)
    status = Column(String(50))
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    email = relationship("Email", back_populates="analysis_logs")

class MLPrediction(Base):
    __tablename__ = 'ml_predictions'

    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey('emails.id', ondelete='CASCADE'))
    predicted_class = Column(String(50))
    probability = Column(Float)
    model_version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    email = relationship("Email", back_populates="ml_predictions")

# Database connection
class Database:
    def __init__(self, db_url=None):
        # Default to SQLite if no URL provided (easier for Windows)
        if db_url is None:
            import os
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'phishing_detector.db')
            db_url = f'sqlite:///{db_path}'

        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        return self.SessionLocal()
