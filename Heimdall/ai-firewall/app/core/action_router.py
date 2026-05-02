from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.scan import ScanRecord
from app.core.redactor import redact

def route_action(
    final_action: str, 
    raw_text: str, 
    detections: list, 
    scan_record: ScanRecord, 
    db: Session
) -> dict:
    """
    Executes the appropriate workflow based on the final_action determined by the policy engine.
    Updates the ScanRecord database model and returns an API response payload.
    """
    
    # Update the record's final action for auditing
    scan_record.final_action = final_action
    
    if final_action == "BLOCK":
        # Update status and immediately reject the request
        scan_record.status = "blocked"
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Policy Violation", 
                "message": "The document contains sensitive entities that trigger a strict BLOCK policy."
            }
        )

    elif final_action == "REDACT":
        # Call the redactor to securely replace entities with placeholders
        redaction_result = redact(raw_text, detections)
        
        # Save the safe, redacted string and update the status
        scan_record.redacted_text = redaction_result["redacted_text"]
        scan_record.status = "processing"
        db.commit()
        
        return {
            "status": scan_record.status,
            "scan_id": scan_record.scan_id,
            "message": "Document redacted securely and is continuing processing."
        }

    elif final_action == "ASK":
        # Pause the pipeline to await manual user consent
        scan_record.status = "awaiting_consent"
        db.commit()
        
        return {
            "status": scan_record.status,
            "scan_id": scan_record.scan_id,
            "message": "Sensitive entities detected. Please hit the consent endpoint to approve or deny.",
            "consent_required": True
        }

    elif final_action == "SUMMARIZE":
        # Pass the document through unchanged, but flag it for the LLM to summarize
        scan_record.status = "ready_for_llm"
        db.commit()
        
        return {
            "status": scan_record.status,
            "scan_id": scan_record.scan_id,
            "message": "Document marked ready for the LLM gateway."
        }

    else:
        # Fallback safeguard
        scan_record.status = "error"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unknown or invalid policy action encountered."
        )
