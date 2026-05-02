from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers import upload, policy, consent, document
from app.database import engine, Base, SessionLocal
from app.models import scan, policy as policy_models, audit
from app.models.policy import Policy, Rule
from app.schemas.policy import ActionEnum
from app.schemas.scan import Severity

app = FastAPI(
    title="Heimdall AI Firewall",
    description="A powerful privacy proxy that intercepts document uploads, detecting and redacting sensitive data before it reaches Language Models.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom exception handler to ensure all HTTP errors return a clean JSON object.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )

# Rebuild / Create all database tables
Base.metadata.create_all(bind=engine)

def seed_default_policy():
    """
    Seeds a comprehensive default policy if one does not already exist.
    This ensures the ASK, BLOCK, and REDACT flows all work out of the box.
    """
    db = SessionLocal()
    try:
        existing = db.query(Policy).filter(Policy.is_default == True).first()
        if existing:
            return  # Already seeded

        default_policy = Policy(name="default", is_default=True)
        db.add(default_policy)
        db.commit()
        db.refresh(default_policy)

        # Define the rule set
        default_rules = [
            # ASK actions — requires user consent before proceeding
            Rule(policy_id=default_policy.id, entity_type="PERSON", action=ActionEnum.ASK, severity=Severity.LOW),
            Rule(policy_id=default_policy.id, entity_type="LOCATION", action=ActionEnum.ASK, severity=Severity.LOW),
            
            # REDACT actions — automatically replaced with placeholders
            Rule(policy_id=default_policy.id, entity_type="PHONE_NUMBER", action=ActionEnum.REDACT, severity=Severity.MEDIUM),
            Rule(policy_id=default_policy.id, entity_type="EMAIL_ADDRESS", action=ActionEnum.REDACT, severity=Severity.MEDIUM),
            Rule(policy_id=default_policy.id, entity_type="IP_ADDRESS", action=ActionEnum.REDACT, severity=Severity.LOW),
            Rule(policy_id=default_policy.id, entity_type="CREDIT_CARD", action=ActionEnum.REDACT, severity=Severity.CRITICAL),
            Rule(policy_id=default_policy.id, entity_type="IFSC_CODE", action=ActionEnum.REDACT, severity=Severity.HIGH),
            
            # BLOCK actions — document is completely rejected
            Rule(policy_id=default_policy.id, entity_type="AADHAAR_NUMBER", action=ActionEnum.BLOCK, severity=Severity.CRITICAL),
            Rule(policy_id=default_policy.id, entity_type="PAN_CARD", action=ActionEnum.BLOCK, severity=Severity.CRITICAL),
        ]

        db.add_all(default_rules)
        db.commit()
        print("✅ Default policy seeded successfully.")
    finally:
        db.close()

seed_default_policy()

# Include the routers
app.include_router(upload.router)
app.include_router(policy.router)
app.include_router(consent.router)
app.include_router(document.router)

@app.get("/")
async def root():
    """
    Root endpoint used for health checks.
    """
    return {
        "status": "success",
        "message": "AI Firewall API is running."
    }
