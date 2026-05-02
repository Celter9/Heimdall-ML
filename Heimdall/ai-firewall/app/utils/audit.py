import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Dict, Any

from app.models.audit import AuditLog

# Setup a standard logger for this module
logger = logging.getLogger(__name__)

def log_event(
    db: Session, 
    event_type: str, 
    scan_id: Optional[str] = None, 
    details: Optional[Dict[str, Any]] = None, 
    ip_address: Optional[str] = None
) -> None:
    """
    Safely creates an AuditLog entry and saves it to the database.
    Contains robust error handling to guarantee that an auditing failure 
    will never crash the primary application workflow.
    """
    try:
        audit_entry = AuditLog(
            event_type=event_type,
            scan_id=scan_id,
            details=details,
            ip_address=ip_address
        )
        
        db.add(audit_entry)
        db.commit()
        
    except SQLAlchemyError as db_error:
        # Rollback is critical here so the broken transaction doesn't poison the SQLAlchemy session
        # for whatever core API endpoint called this function.
        db.rollback()
        logger.error(f"Database Error writing AuditLog '{event_type}': {str(db_error)}")
        
    except Exception as e:
        # Catch-all for anything else (e.g., JSON serialization issues with 'details')
        db.rollback()
        logger.error(f"Unexpected Error writing AuditLog '{event_type}': {str(e)}")
