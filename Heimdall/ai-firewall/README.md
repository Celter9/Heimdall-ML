# 🛡️ Heimdall AI Firewall

> A powerful privacy proxy that intercepts document uploads, automatically detecting and redacting sensitive data before it reaches Language Models. Stop PII leaks at the perimeter while securely enforcing organizational policies and human-in-the-loop consent.

## 📺 Demo

*[Insert Demo GIF Here showing an upload, detection, and redaction process]*

## ✨ Key Features

- **Advanced PII Detection**: Automatically identifies sensitive entities like Aadhaar numbers, PAN cards, phone numbers, and emails using Microsoft Presidio and custom NLP rules.
- **Multi-Format Document Parsing**: Seamlessly extracts raw text from `PDF`, `DOCX`, and `TXT` files while handling complex encodings.
- **Dynamic Policy Engine**: Apply rule-based enforcement to incoming documents. Configure your firewall to instantly **BLOCK**, **REDACT**, **ASK** for consent, or **SUMMARIZE** content based on risk severity.
- **Human-in-the-Loop Consent Flow**: Pauses uncertain or moderately sensitive documents, allowing administrators or users to securely approve, override, or deny the upload before proceeding.

## 🛠️ Tech Stack

- **FastAPI**: Asynchronous, high-performance web framework powering the core API and proxy endpoints.
- **spaCy**: Industrial-strength Natural Language Processing providing the underlying Named Entity Recognition (NER) models.
- **Microsoft Presidio**: The battle-tested detection and anonymization engine used to accurately swap sensitive values for safe placeholders.
- **SQLAlchemy**: Robust Object-Relational Mapping (ORM) for securely tracking policies, scanning states, and maintaining a strict, compliance-ready audit log.

## 🚀 Installation

Follow these steps to deploy the Heimdall AI Firewall locally:

1. **Clone the repository and enter the directory**:
   ```bash
   git clone https://github.com/yourusername/ai-firewall.git
   cd ai-firewall
   ```

2. **Create and activate a Python virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download the necessary NLP model**:
   *Presidio relies on spaCy's large English language model for accurate named entity recognition.*
   ```bash
   python -m spacy download en_core_web_lg
   ```

5. **Start the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

## 🔌 API Usage

Once your server is running (default is `http://127.0.0.1:8000`), you can securely upload a document to the firewall.

### Example Upload Request

```bash
curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_docs/resume_with_pii.pdf"
```

**Example Response**:
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "filename": "resume_with_pii.pdf",
  "message": "Document redacted securely and is continuing processing."
}
```

*For complete, interactive documentation on all endpoints (including Policies, Consent, and Document retrieval), visit `http://127.0.0.1:8000/docs` while the server is active.*
