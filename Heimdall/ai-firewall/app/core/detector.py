import uuid
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import NlpEngineProvider
from app.schemas.scan import DetectionItem, Severity

# Initialize a global AnalyzerEngine using the heavy Transformer Model
configuration = {
    "nlp_engine_name": "transformers",
    "models": [{
        "lang_code": "en",
        "model_name": {
            "spacy": "en_core_web_lg",
            "transformers": "dslim/bert-base-NER"
        }
    }]
}
provider = NlpEngineProvider(nlp_configuration=configuration)
nlp_engine = provider.create_engine()

analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])

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

# 4. Indian Mobile Number (10 digits anywhere, even without word boundaries)
in_mobile_pattern = Pattern(
    name="in_mobile_pattern",
    regex=r"(?<!\d)\d{10}(?!\d)",
    score=0.85
)
in_mobile_recognizer = PatternRecognizer(
    supported_entity="PHONE_NUMBER",
    patterns=[in_mobile_pattern],
    context=["phone", "mobile", "contact"]
)

# Add custom recognizers to the engine registry
analyzer.registry.add_recognizer(aadhaar_recognizer)
analyzer.registry.add_recognizer(pan_recognizer)
analyzer.registry.add_recognizer(ifsc_recognizer)
analyzer.registry.add_recognizer(in_mobile_recognizer)

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

    # Explicitly list the entities we care about. 
    # This prevents Presidio's built-in DATE_TIME or UK_NHS from causing false positives!
    SUPPORTED_ENTITIES = [
        "PERSON", "LOCATION", "NRP", "IP_ADDRESS", 
        "PHONE_NUMBER", "EMAIL_ADDRESS", "CREDIT_CARD", 
        "CRYPTO", "AADHAAR_NUMBER", "PAN_CARD", "IFSC_CODE"
    ]

    # Analyze the text
    presidio_results = analyzer.analyze(text=text, entities=SUPPORTED_ENTITIES, language='en')
    
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
