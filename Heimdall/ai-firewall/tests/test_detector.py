import pytest
from app.core.detector import detect

def test_detect_indian_context_and_standard_entities():
    """
    Test the detect function to ensure it identifies standard Presidio entities
    as well as custom Indian context entities like Aadhaar and PAN cards.
    """
    # Dummy string containing standard and custom entities.
    # Note: Using context words like "pan card" or "aadhaar" boosts confidence scores.
    test_text = (
        "Hello, my name is John Doe and my email is john.doe@example.com. "
        "For KYC verification, my PAN card is ABCDE1234F and my "
        "aadhaar number is 1234 5678 9012."
    )
    
    # Run the detection
    detections = detect(test_text)
    
    # We expect at least 4 detections (PERSON, EMAIL_ADDRESS, PAN_CARD, AADHAAR_NUMBER)
    assert len(detections) >= 4
    
    # Extract all the found entity types into a list for easy assertion
    found_entity_types = [d.entity_type for d in detections]
    
    # Assert standard entities were found
    assert "PERSON" in found_entity_types
    assert "EMAIL_ADDRESS" in found_entity_types
    
    # Assert custom entities were found
    assert "PAN_CARD" in found_entity_types
    assert "AADHAAR_NUMBER" in found_entity_types
    
    # Validate the original values and severities for the custom entities
    pan_detection = next(d for d in detections if d.entity_type == "PAN_CARD")
    assert pan_detection.original_value == "ABCDE1234F"
    assert pan_detection.severity.value == "CRITICAL"
    
    aadhaar_detection = next(d for d in detections if d.entity_type == "AADHAAR_NUMBER")
    assert aadhaar_detection.original_value == "1234 5678 9012"
    assert aadhaar_detection.severity.value == "CRITICAL"

def test_detect_empty_text():
    """
    Test that the detector safely handles empty strings.
    """
    detections = detect("")
    assert len(detections) == 0
