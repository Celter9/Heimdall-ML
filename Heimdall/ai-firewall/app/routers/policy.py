from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.policy import Policy, Rule
from app.schemas.policy import PolicyCreate, PolicyRead

router = APIRouter(
    prefix="/policies",
    tags=["Policies"],
    responses={404: {"description": "Not found"}},
)

@router.post("", response_model=PolicyRead, status_code=status.HTTP_201_CREATED)
def create_policy(policy_in: PolicyCreate, db: Session = Depends(get_db)):
    """
    Create a new policy along with its associated rules.
    """
    # Create the Policy object
    db_policy = Policy(name=policy_in.name, is_default=policy_in.is_default)
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    
    # Create the associated rules
    for rule_in in policy_in.rules:
        db_rule = Rule(
            policy_id=db_policy.id,
            entity_type=rule_in.entity_type,
            action=rule_in.action,
            severity=rule_in.severity
        )
        db.add(db_rule)
    
    db.commit()
    db.refresh(db_policy)
    return db_policy

@router.get("", response_model=List[PolicyRead])
def list_policies(is_default: Optional[bool] = None, db: Session = Depends(get_db)):
    """
    List all policies. Can be filtered by the is_default query parameter.
    """
    query = db.query(Policy)
    if is_default is not None:
        query = query.filter(Policy.is_default == is_default)
    return query.all()

@router.get("/{policy_id}", response_model=PolicyRead)
def get_policy(policy_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific policy by its ID.
    """
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@router.put("/{policy_id}", response_model=PolicyRead)
def update_policy(policy_id: int, policy_in: PolicyCreate, db: Session = Depends(get_db)):
    """
    Update a policy. This will completely replace the old rules with the new rules provided.
    """
    db_policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not db_policy:
        raise HTTPException(status_code=404, detail="Policy not found")
        
    # Update base policy fields
    db_policy.name = policy_in.name
    db_policy.is_default = policy_in.is_default
    
    # Delete existing rules
    db.query(Rule).filter(Rule.policy_id == policy_id).delete()
    
    # Add the new rules
    for rule_in in policy_in.rules:
        db_rule = Rule(
            policy_id=db_policy.id,
            entity_type=rule_in.entity_type,
            action=rule_in.action,
            severity=rule_in.severity
        )
        db.add(db_rule)
        
    db.commit()
    db.refresh(db_policy)
    return db_policy

@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_policy(policy_id: int, db: Session = Depends(get_db)):
    """
    Delete a policy. Prevents deletion if it's the only default policy in the database.
    """
    db_policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not db_policy:
        raise HTTPException(status_code=404, detail="Policy not found")
        
    # Prevent deletion if it's the ONLY default policy
    if db_policy.is_default:
        default_policies_count = db.query(Policy).filter(Policy.is_default == True).count()
        if default_policies_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete the only default policy."
            )
            
    db.delete(db_policy)
    db.commit()
