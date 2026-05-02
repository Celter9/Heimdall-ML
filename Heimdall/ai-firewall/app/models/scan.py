import uuid
from sqlalchemy import Column, String, Integer, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
from app.schemas.scan import Severity

class ScanRecord(Base):
    """
    SQLAlchemy ORM model for storing metadata and text of a document scan.
    """
    __tablename__ = "scan_records"

    # Using String(36) to store UUIDs safely across different databases (like SQLite)
    scan_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    filename = Column(String, index=True)
    status = Column(String, default="processing", index=True)
    risk_score = Column(Integer, nullable=True)
    final_action = Column(String, nullable=True)
    raw_text = Column(Text, nullable=True)
    redacted_text = Column(Text, nullable=True)

    # One-to-Many relationship with detections
    detections = relationship("Detection", back_populates="scan_record", cascade="all, delete-orphan")


class Detection(Base):
    """
    SQLAlchemy ORM model for storing individual entities detected within a scan.
    """
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String(36), ForeignKey("scan_records.scan_id", ondelete="CASCADE"))
    
    entity_type = Column(String, index=True)
    original_value = Column(String)
    placeholder = Column(String, nullable=True)
    
    # Store the integer character indices
    start = Column(Integer)
    end = Column(Integer)
    
    # Store severity using SQLAlchemy Enum mapped to Python Enum
    severity = Column(SQLEnum(Severity))

    # Relationship back to ScanRecord
    scan_record = relationship("ScanRecord", back_populates="detections")
