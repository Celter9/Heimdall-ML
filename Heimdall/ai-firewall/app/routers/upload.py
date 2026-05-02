import uuid
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.file_validator import validate_uploaded_file
from app.core.parser import parse_document
from app.core.detector import detect
from app.core.scorer import calculate_risk_score
from app.core.policy_engine import evaluate
from app.core.action_router import route_action

from app.models.policy import Policy
from app.models.scan import ScanRecord, Detection
from app.schemas.scan import UploadResponse

router = APIRouter(
    tags=["Upload"],
    responses={404: {"description": "Not found"}},
)

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a file for processing.
    Executes the full pipeline: parsing, detection, scoring, policy evaluation, and routing.
    """
    # 1. Validate the file format and size
    validate_uploaded_file(file)
    
    # 2. Read file contents and parse text
    file_bytes = await file.read()
    raw_text = parse_document(file_bytes, file.content_type)
    
    # Initialize the database record early to obtain a valid scan_id
    scan_record = ScanRecord(
        filename=file.filename,
        raw_text=raw_text,
        status="processing"
    )
    db.add(scan_record)
    db.commit()
    db.refresh(scan_record)
    
    # 3. Detect sensitive entities
    detections = detect(raw_text)
    
    # 4. Calculate risk score
    risk_score = calculate_risk_score(detections)
    scan_record.risk_score = risk_score
    db.commit()
    
    # 5. Evaluate detections using the PolicyEngine against the default policy
    default_policy = db.query(Policy).filter(Policy.is_default == True).first()
    if not default_policy:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No default policy is configured in the system. Please create one."
        )
        
    eval_result = evaluate(detections, default_policy)
    final_action = eval_result["final_action"]
    evaluated_detections = eval_result["detections"]
    
    # 6. Save Detection items to the database
    for det in evaluated_detections:
        db_detection = Detection(
            scan_id=scan_record.scan_id,
            entity_type=det.entity_type,
            original_value=det.original_value,
            placeholder=f"<{det.entity_type}>", # Default format used by Presidio Anonymizer
            start=det.start,
            end=det.end,
            severity=det.severity.value if hasattr(det.severity, 'value') else det.severity
        )
        db.add(db_detection)
    db.commit()
    
    # 7. Route the final action (this handles REDACT string updates, BLOCK exceptions, etc.)
    route_response = route_action(
        final_action=final_action,
        raw_text=raw_text,
        detections=evaluated_detections,
        scan_record=scan_record,
        db=db
    )
    
    # 8. Return the final UploadResponse
    return UploadResponse(
        scan_id=scan_record.scan_id,
        status=route_response.get("status", scan_record.status),
        filename=file.filename,
        message=route_response.get("message", "Processing completed.")
    )
