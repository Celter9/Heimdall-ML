from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
from app.schemas.policy import ActionEnum
from app.schemas.scan import Severity

class Policy(Base):
    """
    SQLAlchemy ORM model for the policies table.
    A policy defines a collection of rules for the AI Firewall.
    """
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    is_default = Column(Boolean, default=False)

    # One-to-Many relationship with rules
    rules = relationship("Rule", back_populates="policy", cascade="all, delete-orphan")


class Rule(Base):
    """
    SQLAlchemy ORM model for the rules table.
    A rule maps an entity type and severity to an enforcement action.
    """
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id", ondelete="CASCADE"))
    
    entity_type = Column(String, index=True)
    
    # Store Enums directly using SQLAlchemy's Enum type and Python Enums
    action = Column(SQLEnum(ActionEnum))
    severity = Column(SQLEnum(Severity))

    # Relationship back to Policy
    policy = relationship("Policy", back_populates="rules")
