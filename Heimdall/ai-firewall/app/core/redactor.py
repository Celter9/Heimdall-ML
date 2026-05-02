from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_analyzer import RecognizerResult

# Initialize the global anonymizer engine
anonymizer = AnonymizerEngine()

def redact(text: str, analyzer_results: list) -> dict:
    """
    Redacts sensitive entities from the text based on the provided detection results.
    Returns a dictionary containing the redacted_text string and a list of mapped items.
    """
    if not text or not analyzer_results:
        return {
            "redacted_text": text,
            "items": []
        }

    # Presidio's AnonymizerEngine strictly expects 'RecognizerResult' objects.
    # Since our detector outputs 'DetectionItem' Pydantic models, we dynamically 
    # convert them back into RecognizerResults here if needed.
    presidio_results = []
    for res in analyzer_results:
        if hasattr(res, "entity_type") and hasattr(res, "confidence"):
            presidio_results.append(
                RecognizerResult(
                    entity_type=res.entity_type,
                    start=res.start,
                    end=res.end,
                    score=res.confidence
                )
            )
        else:
            presidio_results.append(res)

    # Define the default anonymization operator.
    # The 'replace' operator without a specific 'new_value' will automatically 
    # replace the sensitive text with its entity type enclosed in angle brackets, 
    # e.g., swapping a name with a <PERSON> placeholder.
    operators = {
        "DEFAULT": OperatorConfig("replace")
    }

    # Run the anonymizer over the text
    anonymized_result = anonymizer.anonymize(
        text=text,
        analyzer_results=presidio_results,
        operators=operators
    )
    
    # Extract the detailed items showing exactly what was replaced and where
    items = []
    for item in anonymized_result.items:
        items.append({
            "entity_type": item.entity_type,
            "start": item.start,
            "end": item.end,
            "placeholder": item.text  # This is the actual <ENTITY> text inserted
        })

    return {
        "redacted_text": anonymized_result.text,
        "items": items
    }
