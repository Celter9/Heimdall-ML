import uuid
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from app.schemas.scan import DetectionItem, Severity

# Initialize a global AnalyzerEngine
analyzer = AnalyzerEngine(supported_languages=["en"])

# --- Custom Recognizers for Indian Context ---

# 1. Aadhaar Number (12 digits, often space-separated)
aadhaar_pattern = Pattern(
    name="aadhaar_pattern",
    regex=r"\b\d{4}\s?\d{4}\s?\d{4}\b",
    score=0.85
)
aadhaar_recognizer = PatternRecognizer(
    supported_entity="AADHAAR_NUMBER",
    patterns=[aadhaar_pattern],
    context=["aadhaar", "uidai"]
)

# 2. PAN Card (5 letters, 4 numbers, 1 letter)
pan_pattern = Pattern(
    name="pan_pattern",
    regex=r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
    score=0.85
)
pan_recognizer = PatternRecognizer(
    supported_entity="PAN_CARD",
    patterns=[pan_pattern],
    context=["pan", "income tax"]
)

# 3. IFSC Code (4 letters, a zero, 6 alphanumeric characters)
ifsc_pattern = Pattern(
    name="ifsc_pattern",
    regex=r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
    score=0.85
)
ifsc_recognizer = PatternRecognizer(
    supported_entity="IFSC_CODE",
    patterns=[ifsc_pattern],
    context=["ifsc", "bank", "branch"]
)

# Add custom recognizers to the engine registry
analyzer.registry.add_recognizer(aadhaar_recognizer)
analyzer.registry.add_recognizer(pan_recognizer)
analyzer.registry.add_recognizer(ifsc_recognizer)

# Map Presidio entity types to Severity enum levels
ENTITY_SEVERITY_MAP = {
    "PERSON": Severity.LOW,
    "LOCATION": Severity.LOW,
    "NRP": Severity.LOW,          # Nationality, religious or political group
    "IP_ADDRESS": Severity.LOW,
    
    "PHONE_NUMBER": Severity.MEDIUM,
    "EMAIL_ADDRESS": Severity.MEDIUM,
    "MEDICAL_LICENSE": Severity.HIGH,
    "US_DRIVER_LICENSE": Severity.HIGH,
    "UK_NHS": Severity.HIGH,
    
    "CREDIT_CARD": Severity.CRITICAL,
    "US_SSN": Severity.CRITICAL,
    "US_BANK_NUMBER": Severity.CRITICAL,
    "IBAN_CODE": Severity.CRITICAL,
    "CRYPTO": Severity.CRITICAL,
    
    # Custom Indian Context Severities
    "AADHAAR_NUMBER": Severity.CRITICAL,
    "PAN_CARD": Severity.CRITICAL,
    "IFSC_CODE": Severity.HIGH
}

def detect(text: str) -> list[DetectionItem]:
    """
    Runs the text through the Presidio analyzer and maps the results to Pydantic models.
    """
    if not text:
        return []

    # Analyze the text (entities=None will use all supported entities in the registry)
    presidio_results = analyzer.analyze(text=text, entities=None, language='en')
    
    detection_items = []
    
    for result in presidio_results:
        # Extract the exact string that triggered the detection
        original_value = text[result.start:result.end]
        
        # Look up severity, default to MEDIUM if the entity is not in the map
        severity = ENTITY_SEVERITY_MAP.get(result.entity_type, Severity.MEDIUM)
        
        # Suggest an action based on severity
        suggested_action = "REDACT" if severity in (Severity.CRITICAL, Severity.HIGH) else "REVIEW"
        
        # Map to Pydantic model
        detection_items.append(DetectionItem(
            detection_id=uuid.uuid4(),
            entity_type=result.entity_type,
            original_value=original_value,
            start=result.start,
            end=result.end,
            confidence=result.score,
            severity=severity,
            suggested_action=suggested_action
        ))
        
    return detection_items
