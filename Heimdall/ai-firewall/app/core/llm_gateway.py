import httpx
from fastapi import HTTPException, status
from app.config import settings
from app.core.detector import detect
from app.core.redactor import redact

async def process_with_llm(user_prompt: str, redacted_text: str) -> str:
    """
    Sends the user's prompt and the safely redacted document to the OpenAI API.
    Acts as an outbound "Response Filter" by scanning and redacting the AI's 
    response before returning it to the user.
    """
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OPENAI_API_KEY is not configured in the environment settings."
        )

    # 1. Prepare the payload for OpenAI
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o-mini", # Standard lightweight model
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant analyzing a document. "
                    "The document has had sensitive information safely replaced with placeholders (e.g., <PERSON>). "
                    "Use the exact placeholders naturally in your response when referring to those entities."
                )
            },
            {
                "role": "user",
                "content": f"Document Text:\n{redacted_text}\n\nUser Request:\n{user_prompt}"
            }
        ],
        "temperature": 0.3
    }

    # 2. Make the asynchronous HTTP request to the LLM provider
    async with httpx.AsyncClient(timeout=45.0) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"OpenAI API Error: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Network Error reaching OpenAI API: {str(e)}"
            )

    # Extract the raw response string from the JSON payload
    response_data = response.json()
    raw_ai_response = response_data["choices"][0]["message"]["content"]

    # 3. RESPONSE FILTER: The outbound AI text must be scanned for leaked PII
    # We pass the raw response back through our core detector
    outbound_detections = detect(raw_ai_response)
    
    # We immediately redact any newly generated or leaked PII
    redaction_result = redact(raw_ai_response, outbound_detections)
    safe_final_response = redaction_result["redacted_text"]

    return safe_final_response
