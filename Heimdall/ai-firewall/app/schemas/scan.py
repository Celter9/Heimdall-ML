from enum import Enum
import uuid
from pydantic import BaseModel, Field
from typing import Optional

class Severity(str, Enum):
    """
    Enum representing the severity of a detected issue.
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class DetectionItem(BaseModel):
    """
    Pydantic model representing a single detected issue within a scanned document.
    """
    detection_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique identifier for this detection")
    entity_type: str = Field(description="The type of entity detected (e.g., PII, MALICIOUS_URL)")
    original_value: str = Field(description="The original text snippet that triggered the detection")
    start: int = Field(description="The starting character index of the detection in the original text")
    end: int = Field(description="The ending character index of the detection in the original text")
    confidence: float = Field(description="Confidence score of the detection (0.0 to 1.0)")
    severity: Severity = Field(description="The assigned severity level of the detection")
    suggested_action: Optional[str] = Field(default=None, description="An optional recommended action (e.g., REDACT, BLOCK)")

class UploadResponse(BaseModel):
    """
    Schema for the response returned after successfully uploading and processing a document.
    """
    scan_id: str
    status: str
    filename: str
    message: Optional[str] = None
