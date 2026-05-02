from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ConsentRequest(BaseModel):
    """
    Schema for a user submitting a consent decision for a flagged document.
    """
    scan_id: str = Field(description="The unique identifier of the scan awaiting consent.")
    approved: bool = Field(description="Boolean indicating whether the user approves or denies the document.")
    overrides: Optional[Dict[str, Any]] = Field(default=None, description="Optional dictionary for providing specific overrides.")
    user_note: Optional[str] = Field(default=None, description="Optional justification or note provided by the user.")

class ConsentResponse(BaseModel):
    """
    Schema for the response returned after successfully processing a consent request.
    """
    scan_id: str
    decision: str = Field(description="The recorded decision (e.g., 'APPROVED', 'DENIED').")
    next_status: str = Field(description="The new status of the document scan (e.g., 'processing', 'rejected').")
    message: str
