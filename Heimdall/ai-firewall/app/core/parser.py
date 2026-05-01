import io
import pdfplumber
from pdfminer.pdfdocument import PDFPasswordIncorrect
import docx
from docx.opc.exceptions import PackageNotFoundError
from fastapi import HTTPException, status

def parse_pdf(file_bytes: bytes) -> str:
    text_content = []
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
    except PDFPasswordIncorrect:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PASSWORD_PROTECTED_PDF"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"PARSE_ERROR: {str(e)}"
        )
    
    return "\n".join(text_content)

def parse_docx(file_bytes: bytes) -> str:
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        text_content = [paragraph.text for paragraph in doc.paragraphs if paragraph.text]
        return "\n".join(text_content)
    except PackageNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PARSE_ERROR: Invalid DOCX file format."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"PARSE_ERROR: {str(e)}"
        )

def parse_txt(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PARSE_ERROR: Failed to decode TXT file. Ensure it is UTF-8 encoded."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"PARSE_ERROR: {str(e)}"
        )

def parse_document(file_bytes: bytes, mime_type: str) -> str:
    """
    Routes the file bytes to the correct parser based on MIME type.
    Raises exceptions for errors like password protection, parse failures, or empty content.
    """
    if mime_type == "application/pdf":
        text = parse_pdf(file_bytes)
    elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = parse_docx(file_bytes)
    elif mime_type == "text/plain":
        text = parse_txt(file_bytes)
    else:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="PARSE_ERROR: Unsupported file type."
        )
    
    # Check if the extracted text is empty or only whitespace
    if not text or not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="EMPTY_DOCUMENT"
        )
        
    return text
