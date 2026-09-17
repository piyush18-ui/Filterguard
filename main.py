"""
FastAPI backend for the Multimodal Phishing & Social Engineering Detector.

Run with:
    uvicorn main:app --reload --port 8000

Requires ANTHROPIC_API_KEY to be set in the environment (see .env.example).
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rules import extract_evidence
from llm_reasoning import assess_message
from sample_data import SAMPLE_MESSAGES

app = FastAPI(title="Phishing & Social Engineering Detector")

# Allow the React dev server to call this API during local development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessageInput(BaseModel):
    subject: str = ""
    body: str
    sender_email: str = ""
    attachment_filename: str | None = None


class AnalysisResponse(BaseModel):
    risk_level: str
    confidence: str
    top_factors: list[str]
    recommended_action: str
    reasoning_summary: str
    evidence: dict


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/samples")
def get_samples():
    """Returns bundled demo messages for quick testing without typing input."""
    return SAMPLE_MESSAGES


@app.post("/analyze", response_model=AnalysisResponse)
def analyze(payload: MessageInput):
    if not payload.body.strip():
        raise HTTPException(status_code=400, detail="Message body cannot be empty.")

    evidence = extract_evidence(
        subject=payload.subject,
        body=payload.body,
        sender_email=payload.sender_email,
        attachment_filename=payload.attachment_filename,
    )

    full_text = f"Subject: {payload.subject}\nFrom: {payload.sender_email}\n\n{payload.body}"

    try:
        assessment = assess_message(full_text, evidence)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Reasoning layer failed: {str(e)}")

    return {
        **assessment,
        "evidence": evidence,
    }
