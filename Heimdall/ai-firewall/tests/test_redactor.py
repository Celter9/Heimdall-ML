import pytest
from app.core.redactor import redact
from app.schemas.scan import DetectionItem, Severity

def test_redact_function_replaces_entities_correctly():
    """
    Test that the redact function successfully replaces sensitive data with 
    appropriate <ENTITY_TYPE> placeholders and strips out the original text.
    """
    
    # Define our raw dummy text
    test_text = "Hello, my name is John Doe and my phone number is 555-123-4567."
    
    # Let's verify the indexes manually to ensure a valid test setup
    assert test_text[18:26] == "John Doe"
    assert test_text[50:62] == "555-123-4567"

    # Create dummy detections mirroring what the detector outputs
    dummy_detections = [
        DetectionItem(
            entity_type="PERSON",
            original_value="John Doe",
            start=18,
            end=26,
            confidence=0.99,
            severity=Severity.LOW
        ),
        DetectionItem(
            entity_type="PHONE_NUMBER",
            original_value="555-123-4567",
            start=50,
            end=62,
            confidence=0.99,
            severity=Severity.MEDIUM
        )
    ]
    
    # Run the redaction process
    result = redact(test_text, dummy_detections)
    redacted_text = result["redacted_text"]
    
    # 1. Assert that the sensitive data is STRICTLY absent from the result
    assert "John Doe" not in redacted_text
    assert "555-123-4567" not in redacted_text
    
    # 2. Assert that the correct placeholders were successfully inserted
    assert "<PERSON>" in redacted_text
    assert "<PHONE_NUMBER>" in redacted_text
    
    # 3. Assert the exact expected final string matches
    expected_string = "Hello, my name is <PERSON> and my phone number is <PHONE_NUMBER>."
    assert redacted_text == expected_string

def test_redact_handles_empty_inputs():
    """
    Test that passing empty strings or empty detections is safely handled.
    """
    # Empty detections list should return the original string unaltered
    result = redact("Safe text", [])
    assert result["redacted_text"] == "Safe text"
    
    # Empty string should return empty
    result = redact("", [])
    assert result["redacted_text"] == ""
