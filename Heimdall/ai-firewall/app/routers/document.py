from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.scan import ScanRecord

router = APIRouter(
    tags=["Document"],
    responses={404: {"description": "Not found"}},
)

@router.get("/document/{scan_id}/redacted")
def get_redacted_document(scan_id: str, db: Session = Depends(get_db)):
    """
    Retrieve the fully redacted text of a completed document scan.
    Returns a 404 error if the document is still processing, blocked, or awaiting consent.
    """
    # Query the database for the scan record
    scan_record = db.query(ScanRecord).filter(ScanRecord.scan_id == scan_id).first()
    
    if not scan_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Scan record not found in the database."
        )
        
    # Strictly enforce the status check
    if scan_record.status != "complete":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not ready. The pipeline is either still processing, paused, or blocked."
        )
        
    # Return the clean, safe text
    return {
        "scan_id": scan_record.scan_id,
        "redacted_text": scan_record.redacted_text
    }
