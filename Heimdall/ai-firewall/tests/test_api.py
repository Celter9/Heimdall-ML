import io
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal, Base, engine
from app.models.policy import Policy

client = TestClient(app)

@pytest.fixture(autouse=True)
def ensure_default_policy():
    """
    Ensure the database has a default policy before testing.
    This prevents the /upload endpoint from failing with a 500 error due to missing configuration.
    """
    # Ensure tables are built
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if a default policy exists
        if not db.query(Policy).filter(Policy.is_default == True).first():
            # Create a basic default policy if missing
            policy = Policy(name="Auto-Generated Test Policy", is_default=True)
            db.add(policy)
            db.commit()
    finally:
        db.close()

def test_upload_endpoint_processes_file():
    """
    End-to-End test simulating a user uploading a document with sensitive data.
    """
    # Generate a dummy .txt file in-memory
    dummy_text = "My name is John Doe and my Aadhaar number is 1234 5678 9012."
    file_bytes = dummy_text.encode('utf-8')
    
    # Package it as multipart/form-data
    files = {
        "file": ("dummy_test_doc.txt", io.BytesIO(file_bytes), "text/plain")
    }
    
    # POST to the /upload endpoint
    response = client.post("/upload", files=files)
    
    # The response depends on how the active policy evaluates the Aadhaar number.
    # If it evaluates to 'REDACT' or 'SUMMARIZE', we get a 200 OK.
    if response.status_code == 200:
        data = response.json()
        assert "scan_id" in data
        assert "filename" in data
        assert "status" in data
        assert data["filename"] == "dummy_test_doc.txt"
    # If the active policy evaluates to 'BLOCK', we gracefully get a 403 Forbidden.
    elif response.status_code == 403:
        assert "error" in response.json()
    else:
        pytest.fail(f"Unexpected API response: {response.status_code} - {response.text}")

def test_get_redacted_document_invalid_id():
    """
    Test the retrieval endpoint to ensure it properly blocks unknown scan IDs.
    """
    invalid_uuid = "11111111-2222-3333-4444-555555555555"
    response = client.get(f"/document/{invalid_uuid}/redacted")
    
    # Assert it returns a 404
    assert response.status_code == 404
    # Assert our custom exception handler caught it and formatted the error
    assert "error" in response.json()
