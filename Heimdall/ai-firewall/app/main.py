from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from app.routers import upload, policy, consent, document
from app.database import engine, Base
from app.models import scan, policy as policy_models, audit

app = FastAPI(
    title="Heimdall AI Firewall",
    description="A powerful privacy proxy that intercepts document uploads, detecting and redacting sensitive data before it reaches Language Models.",
    version="1.0.0",
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
