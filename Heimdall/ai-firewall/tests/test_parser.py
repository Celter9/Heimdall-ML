import io
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
import docx

from app.core.parser import parse_txt, parse_docx, parse_pdf, parse_document

def create_dummy_docx(text: str) -> bytes:
    """Helper to generate a valid in-memory DOCX file."""
    doc = docx.Document()
    doc.add_paragraph(text)
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

def test_parse_txt_success():
    text = "Hello TXT World"
    file_bytes = text.encode("utf-8")
    result = parse_txt(file_bytes)
    assert result == text

def test_parse_docx_success():
    text = "Hello DOCX World"
    file_bytes = create_dummy_docx(text)
    result = parse_docx(file_bytes)
    assert result == text

@patch("app.core.parser.pdfplumber.open")
def test_parse_pdf_success(mock_pdfplumber):
    """
    Mock pdfplumber for PDF extraction, since generating a truly 
    valid minimal PDF byte string from scratch is brittle.
    """
    mock_pdf = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Hello PDF World"
    mock_pdf.pages = [mock_page]
    mock_pdfplumber.return_value.__enter__.return_value = mock_pdf

    result = parse_pdf(b"fake pdf bytes")
    assert result == "Hello PDF World"

def test_parse_document_unsupported_mime():
    with pytest.raises(HTTPException) as exc_info:
        parse_document(b"fake image bytes", "image/png")
    
    assert exc_info.value.status_code == 415
    assert "Unsupported file type" in str(exc_info.value.detail)

def test_parse_document_empty_content():
    """Testing the global check for empty documents across any valid mime type."""
    with pytest.raises(HTTPException) as exc_info:
        # The parser will return whitespace which triggers the empty check
        parse_document(b"   ", "text/plain")
        
    assert exc_info.value.status_code == 400
    assert "EMPTY_DOCUMENT" in str(exc_info.value.detail)

def test_parse_document_routing():
    """Ensure parse_document routes correctly using the TXT parser as a proxy."""
    file_bytes = "Routing works!".encode("utf-8")
    result = parse_document(file_bytes, "text/plain")
    assert result == "Routing works!"
