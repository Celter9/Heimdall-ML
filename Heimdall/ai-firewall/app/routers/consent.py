from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.scan import ScanRecord, Detection
from app.models.audit import AuditLog
from app.schemas.consent import ConsentRequest, ConsentResponse
from app.core.action_router import route_action

router = APIRouter(
    tags=["Consent"],
    responses={404: {"description": "Not found"}},
)

@router.post("/scan/{scan_id}/consent", response_model=ConsentResponse)
async def submit_consent(
    scan_id: str, 
    consent_request: ConsentRequest, 
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Process a user's consent decision for a flagged document scan.
    """
    # 1. Fetch the ScanRecord
    scan_record = db.query(ScanRecord).filter(ScanRecord.scan_id == scan_id).first()
    if not scan_record:
        raise HTTPException(status_code=404, detail="ScanRecord not found")
        
    # Ensure it's in the correct state
    if scan_record.status != "awaiting_consent":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Scan is currently in '{scan_record.status}' status, expected 'awaiting_consent'."
        )

    # 2. Prepare AuditLog entry
    client_ip = request.client.host if request.client else "Unknown"
    audit_log = AuditLog(
        scan_id=scan_id,
        ip_address=client_ip,
        details={
            "overrides": consent_request.overrides,
            "user_note": consent_request.user_note
        }
    )

    if not consent_request.approved:
        # 3. If denied, securely block the document
        scan_record.status = "blocked"
        audit_log.event_type = "CONSENT_DENIED"
        
        db.add(audit_log)
        db.commit()
        
        return ConsentResponse(
            scan_id=scan_id,
            decision="DENIED",
            next_status=scan_record.status,
            message="Consent denied. The document has been blocked."
        )
    else:
        # 4. If approved, apply overrides and resume processing
        audit_log.event_type = "CONSENT_APPROVED"
        db.add(audit_log) # Stage log so it commits when route_action commits
        
        # Fetch the detections associated with this scan
        detections = db.query(Detection).filter(Detection.scan_id == scan_id).all()
        
        # Apply any detection overrides provided by the user
        if consent_request.overrides:
            for det in detections:
                if det.entity_type in consent_request.overrides:
                    # We assume overrides map an entity_type to a custom placeholder string
                    det.placeholder = consent_request.overrides[det.entity_type]
        
        # 5. Trigger the action router to resume processing for the LLM gateway.
        # We explicitly pass "SUMMARIZE" to set status to 'ready_for_llm'
        route_action(
            final_action="SUMMARIZE",
            raw_text=scan_record.raw_text,
            detections=detections,
            scan_record=scan_record,
            db=db
        )
        
        return ConsentResponse(
            scan_id=scan_id,
            decision="APPROVED",
            next_status=scan_record.status,
            message="Consent approved. Document has been queued for the LLM gateway."
        )
