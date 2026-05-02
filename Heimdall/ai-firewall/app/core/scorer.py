from typing import List
from app.schemas.scan import DetectionItem

SEVERITY_WEIGHTS = {
    'CRITICAL': 25,
    'HIGH': 15,
    'MEDIUM': 8,
    'LOW': 3
}

def calculate_risk_score(detections: List[DetectionItem]) -> int:
    """
    Calculates an aggregate risk score by summing the weights of each detection's severity.
    The final score is capped at a maximum of 100.
    """
    total_score = 0
    
    for detection in detections:
        # Extract the string value from the Severity Enum to look up the weight
        severity_key = detection.severity.value
        weight = SEVERITY_WEIGHTS.get(severity_key, 0)
        total_score += weight
        
    # Cap the score at 100
    return min(total_score, 100)

def get_risk_level(score: int) -> str:
    """
    Returns the qualitative risk level category based on the numerical score.
    """
    if score <= 20:
        return 'LOW'
    elif score <= 50:
        return 'MEDIUM'
    elif score <= 75:
        return 'HIGH'
    else:
        return 'CRITICAL'
