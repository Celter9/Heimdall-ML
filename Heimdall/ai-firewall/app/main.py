from fastapi import FastAPI
from app.routers import upload

app = FastAPI(
    title="AI Firewall API",
    description="API for scanning and validating documents.",
    version="1.0.0",
)

# Include the routers
app.include_router(upload.router)

@app.get("/")
async def root():
    """
    Root endpoint used for health checks.
    """
    return {
        "status": "success",
        "message": "AI Firewall API is running."
    }
