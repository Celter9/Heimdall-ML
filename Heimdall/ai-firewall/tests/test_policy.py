import pytest
from app.core.scorer import calculate_risk_score
from app.core.policy_engine import evaluate
from app.schemas.scan import DetectionItem, Severity
from app.schemas.policy import PolicyRead, RuleRead, ActionEnum

def test_calculate_risk_score_cap():
    """
    Ensure the calculated risk score never exceeds the maximum cap of 100,
    even if the total severity weights sum up to a value > 100.
    """
    # Create 6 CRITICAL detections (weight: 25 * 6 = 150)
    detections = [
        DetectionItem(
            entity_type="CREDIT_CARD",
            original_value="fake_cc",
            start=0,
            end=7,
            confidence=0.99,
            severity=Severity.CRITICAL
        ) for _ in range(6)
    ]
    
    score = calculate_risk_score(detections)
    
    # Assert the score is strictly capped at 100
    assert score == 100


def test_evaluate_strictest_action():
    """
    Test that the policy engine attaches the correct individual action to each detection,
    and returns the strictest action (e.g., BLOCK > REDACT) for the entire document.
    """
    # Create a dummy policy via the Pydantic schema
    dummy_policy = PolicyRead(
        id=1,
        name="Test Strict Policy",
        is_default=True,
        rules=[
            RuleRead(
                id=101,
                policy_id=1,
                entity_type="CREDIT_CARD",
                action=ActionEnum.BLOCK,
                severity=Severity.CRITICAL
            ),
            RuleRead(
                id=102,
                policy_id=1,
                entity_type="PERSON",
                action=ActionEnum.REDACT,
                severity=Severity.LOW
            )
        ]
    )
    
    # Create dummy detections to feed into the engine
    detections = [
        DetectionItem(
            entity_type="CREDIT_CARD",
            original_value="1234",
            start=0, end=4,
            confidence=0.95,
            severity=Severity.CRITICAL
        ),
        DetectionItem(
            entity_type="PERSON",
            original_value="John",
            start=5, end=9,
            confidence=0.85,
            severity=Severity.LOW
        ),
        # This third item has no matching rule in the policy, testing the default fallback
        DetectionItem(
            entity_type="IP_ADDRESS",
            original_value="127.0.0.1",
            start=10, end=19,
            confidence=0.99,
            severity=Severity.LOW
        )
    ]
    
    # Run the evaluation
    result = evaluate(detections, dummy_policy)
    
    # 1. Assert that the final action bubbled up the strictest rule (BLOCK)
    assert result["final_action"] == ActionEnum.BLOCK.value
    
    # 2. Assert that the individual suggested actions were properly attached
    evaluated_detections = result["detections"]
    assert evaluated_detections[0].suggested_action == ActionEnum.BLOCK.value
    assert evaluated_detections[1].suggested_action == ActionEnum.REDACT.value
    
    # 3. Assert that the unmatched entity defaulted to REDACT
    assert evaluated_detections[2].suggested_action == ActionEnum.REDACT.value
