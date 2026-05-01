import uuid
from fastapi import APIRouter, File, UploadFile
from app.utils.file_validator import validate_uploaded_file
from app.core.parser import parse_document

router = APIRouter(
    tags=["Upload"],
    responses={404: {"description": "Not found"}},
)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file for processing.
    The file is validated for format and size constraints.
    Returns a dummy scan ID for tracking.
    """
    # 1. Validate the file format and size
    validate_uploaded_file(file)
    
    # 2. Read file contents and extract text
    file_bytes = await file.read()
    extracted_text = parse_document(file_bytes, file.content_type)
    
    # 3. Return a successful response with dummy scan_id
    # We use uuid4 to simulate a real database-generated or task-generated ID
    scan_id = str(uuid.uuid4())
    
    return {
        "scan_id": scan_id,
        "status": "processing",
        "filename": file.filename,
        "text_length": len(extracted_text)
    }
