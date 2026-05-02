from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from enum import Enum
from app.schemas.scan import Severity

class ActionEnum(str, Enum):
    """
    Actions that can be taken when a rule triggers.
    """
    BLOCK = "BLOCK"
    REDACT = "REDACT"
    ASK = "ASK"
    SUMMARIZE = "SUMMARIZE"

# --- Rule Schemas ---
class RuleBase(BaseModel):
    entity_type: str
    action: ActionEnum
    severity: Severity

class RuleCreate(RuleBase):
    """Schema for creating a new Rule"""
    pass

class RuleRead(RuleBase):
    """Schema for returning a Rule from the database"""
    id: int
    policy_id: int
    
    model_config = ConfigDict(from_attributes=True)

# --- Policy Schemas ---
class PolicyBase(BaseModel):
    name: str
    is_default: bool = False

class PolicyCreate(PolicyBase):
    """Schema for creating a new Policy with its Rules"""
    rules: List[RuleCreate] = []

class PolicyRead(PolicyBase):
    """Schema for returning a Policy from the database"""
    id: int
    rules: List[RuleRead] = []
    
    model_config = ConfigDict(from_attributes=True)
