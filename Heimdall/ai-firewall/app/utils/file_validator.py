from fastapi import UploadFile, HTTPException, status

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

ALLOWED_MIME_TYPES = {
    "application/pdf",  # PDF
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # DOCX
    "text/plain"  # TXT
}

def validate_uploaded_file(file: UploadFile) -> None:
    """
    Validates an uploaded file's MIME type and size.
    Raises an HTTPException if validation fails.
    """
    # 1. Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {file.content_type}. Allowed types are PDF, DOCX, and TXT."
        )

    # 2. Validate file size
    # In newer versions of FastAPI, file.size is available and accurate
    if file.size is not None:
        if file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds the 20 MB limit."
            )
    else:
        # Fallback to check file size manually if file.size is None
        file.file.seek(0, 2)  # Seek to the end of the file
        file_size = file.file.tell()  # Get the current position (file size)
        file.file.seek(0)  # Reset the file pointer to the beginning
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds the 20 MB limit."
            )
