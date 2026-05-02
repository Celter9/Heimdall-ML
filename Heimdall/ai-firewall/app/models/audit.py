import uuid
import datetime
from sqlalchemy import Column, String, JSON, DateTime
from app.database import Base

class AuditLog(Base):
    """
    SQLAlchemy ORM model for recording an audit trail of events in the AI Firewall.
    """
    __tablename__ = "audit_logs"

    # Using String(36) to safely store UUIDs across different database dialects (like SQLite)
    log_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    event_type = Column(String, index=True, nullable=False)
    scan_id = Column(String(36), index=True, nullable=True)
    
    # JSON type allows storing flexible metadata like overrides, notes, or headers
    details = Column(JSON, nullable=True)
    
    ip_address = Column(String, nullable=True)
    
    # Automatically timestamp the log entry upon creation
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
