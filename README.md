# AI Firewall for Document Uploads

> A privacy proxy that intercepts every document upload, detects sensitive data, scores risk, enforces policy rules, and decides what the Language Model is allowed to see.

## Architecture

```mermaid
flowchart TB
    %% ── External Actors ──
    Client["🖥️ Client / Frontend UI"]
    LLM["🤖 External LLM API"]

    %% ── API Layer ──
    subgraph API["FastAPI Application Layer"]
        direction TB
        Upload["/upload Endpoint"]
        PolicyAPI["/policy Endpoints"]
        ConsentAPI["/consent Endpoints"]
        DocAPI["/documents Endpoints"]
    end

    %% ── Core Processing Pipeline ──
    subgraph Pipeline["Core Processing Pipeline"]
        direction TB
        Validator["📋 File Validator\n(type & size checks)"]
        Parser["📄 Document Parser\n(PDF · DOCX · TXT)"]
        Detector["🔍 PII Detector\n(Presidio + spaCy NER)"]
        Scorer["📊 Risk Scorer\n(0–100 severity score)"]
        PolicyEng["⚖️ Policy Engine\n(rule matching)"]
        ActionRouter{"🚦 Action Router"}
    end

    %% ── Action Branches ──
    subgraph Actions["Policy Actions"]
        direction TB
        Block["🛑 BLOCK\nReject upload entirely"]
        Redact["✏️ REDACT\nReplace PII with placeholders"]
        Ask["❓ ASK\nAwait user consent"]
        Summarize["📝 SUMMARIZE\nMark for LLM summary"]
    end

    %% ── Supporting Services ──
    subgraph Services["Supporting Services"]
        direction TB
        Redactor["🔒 Presidio Anonymizer"]
        Gateway["🌐 LLM Gateway\n(async httpx)"]
    end

    %% ── Persistence ──
    subgraph DB["Persistence Layer"]
        direction LR
        SQLite[("🗄️ SQLite DB")]
        AuditLog["📜 Audit Logger"]
    end

    %% ── Flow Connections ──
    Client -- "File Upload (PDF/DOCX/TXT)" --> Upload
    Client -- "Manage Rules" --> PolicyAPI
    Client -- "Approve / Deny" --> ConsentAPI
    Client -- "View Results" --> DocAPI

    Upload --> Validator
    Validator --> Parser
    Parser -- "Extracted Text" --> Detector
    Detector -- "Entity List" --> Scorer
    Scorer -- "Risk Score" --> PolicyEng
    PolicyEng -- "Final Action" --> ActionRouter

    ActionRouter -- "BLOCK" --> Block
    ActionRouter -- "REDACT" --> Redact
    ActionRouter -- "ASK" --> Ask
    ActionRouter -- "SUMMARIZE" --> Summarize

    Redact --> Redactor
    Redactor -- "Sanitized Text" --> Gateway
    Summarize --> Gateway
    Gateway -- "Safe Payload" --> LLM
    LLM -- "LLM Response" --> Gateway

    Ask -- "Consent Flow" --> ConsentAPI

    %% ── Audit Trail ──
    Upload -. "log" .-> AuditLog
    ActionRouter -. "log" .-> AuditLog
    AuditLog --> SQLite
    Upload -. "scan record" .-> SQLite

    %% ── Styling ──
    classDef apiStyle fill:#4f46e5,stroke:#3730a3,color:#fff
    classDef pipelineStyle fill:#0891b2,stroke:#0e7490,color:#fff
    classDef actionBlock fill:#dc2626,stroke:#b91c1c,color:#fff
    classDef actionRedact fill:#f59e0b,stroke:#d97706,color:#000
    classDef actionAsk fill:#8b5cf6,stroke:#7c3aed,color:#fff
    classDef actionSumm fill:#10b981,stroke:#059669,color:#fff
    classDef serviceStyle fill:#6366f1,stroke:#4f46e5,color:#fff
    classDef dbStyle fill:#334155,stroke:#1e293b,color:#fff
    classDef externalStyle fill:#1e293b,stroke:#0f172a,color:#fff

    class Upload,PolicyAPI,ConsentAPI,DocAPI apiStyle
    class Validator,Parser,Detector,Scorer,PolicyEng,ActionRouter pipelineStyle
    class Block actionBlock
    class Redact actionRedact
    class Ask actionAsk
    class Summarize actionSumm
    class Redactor,Gateway serviceStyle
    class SQLite,AuditLog dbStyle
    class Client,LLM externalStyle
```

## Features

- **5+ Entity Types Detected**: Identifies critical entities including PERSON, ORG, LOCATION, PHONE_NUMBER, and custom Indian PII like AADHAAR.
- **4 Proxy Actions**: Policy engine enforces actions based on sensitivity: **BLOCK**, **ASK** (Human-in-the-Loop), **REDACT**, and **SUMMARIZE**.
- **Risk Scoring**: Evaluates risk from 0–100 (LOW to CRITICAL) depending on the severity and count of the PII found.
- **Audit Log**: Compliance-ready logging using SQLAlchemy to track every upload, detection, action, and LLM response.
- **Document Parsing**: Seamless extraction from PDF, DOCX, and TXT files using specialized tools.

## Tech Stack

| Component | Technology | Responsibility |
| :--- | :--- | :--- |
| **Upload & Consent API** | FastAPI, Pydantic | Receives files, validates schema, handles consent flows |
| **Document Parser** | pdfplumber, python-docx | Extracts text from PDFs and DOCX files |
| **PII Detector** | presidio-analyzer, spaCy | Identifies sensitive entities (Named Entity Recognition) |
| **Risk Scorer & Policy Engine**| Python custom logic | Assigns risk scores and maps entity types to actions |
| **Redactor** | presidio-anonymizer | Replaces PII with safe placeholders |
| **LLM Gateway** | httpx (async) | Safely sends sanitized text to the LLM |
| **Database & Audit** | SQLAlchemy, SQLite | Logs all events and scan records |

## Quickstart

```bash
# 1. Clone the repository and navigate into the project
git clone https://github.com/yourusername/ai-firewall.git
cd ai-firewall

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Download the necessary spaCy model for NLP
python -m spacy download en_core_web_lg

# 4. Start the FastAPI development server
uvicorn app.main:app --reload
```

## API Docs

The interactive API documentation is automatically generated. Once the server is running, navigate to:
[http://localhost:8000/docs](http://localhost:8000/docs)

<!-- Add screenshot of /docs here -->

## Running Tests

![Coverage Badge](https://img.shields.io/badge/coverage-80%25-brightgreen)

Execute the comprehensive test suite to ensure all components and the detection engine are functioning correctly:

```bash
pytest tests/ --cov=app --cov-report=term-missing
```