from typing import List, Dict, Any
from app.schemas.scan import DetectionItem
from app.schemas.policy import ActionEnum

# Priority mapping: Higher integer means a stricter action
ACTION_PRIORITY = {
    ActionEnum.BLOCK: 4,
    ActionEnum.ASK: 3,
    ActionEnum.SUMMARIZE: 2,
    ActionEnum.REDACT: 1
}

def evaluate(detections: List[DetectionItem], policy) -> Dict[str, Any]:
    """
    Evaluates a list of detections against the rules in the provided policy.
    Attaches a suggested_action to each detection, and calculates the final 
    strictest action for the entire document.
    """
    # Create a lookup mapping of entity_type -> action for O(1) rule matching
    rule_map = {rule.entity_type: rule.action for rule in policy.rules}
    
    # Baseline default action for the document
    final_action = ActionEnum.REDACT 
    highest_priority = ACTION_PRIORITY[final_action]
    
    for detection in detections:
        # Check the policy for a rule matching this entity type.
        # If no rule matches, default to REDACT.
        action = rule_map.get(detection.entity_type, ActionEnum.REDACT)
        
        # Ensure it's an ActionEnum instance (in case the DB returned a raw string)
        if isinstance(action, str):
            action = ActionEnum(action)
            
        # Attach the suggested action to the detection model
        detection.suggested_action = action.value
        
        # Determine if this action is stricter than our current document final_action
        priority = ACTION_PRIORITY[action]
        if priority > highest_priority:
            final_action = action
            highest_priority = priority
            
    return {
        "final_action": final_action.value,
        "detections": detections
    }
