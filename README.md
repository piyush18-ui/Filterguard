# Multimodal Phishing & Social Engineering Detector

Hackathon prototype for HackIndore 4.0 — Cybersecurity PS1.

## How it works

Two-layer architecture:

1. **Rule-based signal extraction** (`backend/rules.py`) — fast, deterministic,
   explainable checks: sender domain mismatch, suspicious URLs, urgency/threat/
   reward language, sensitive-info requests, generic greetings, suspicious
   attachments.

2. **LLM reasoning layer** (`backend/llm_reasoning.py`) — Claude reasons over
   the combined evidence like a human analyst would, weighing combinations of
   signals rather than triggering on any single one, and produces a structured
   verdict: risk level, confidence, top factors, recommended action, and a
   plain-language explanation.

This combo means you get explainability (from the rules) AND contextual
nuance (from the LLM) — satisfying the "explainable reasoning, not a
black box" requirement in the problem statement.

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and add your ANTHROPIC_API_KEY
export $(cat .env | xargs)   # or use python-dotenv / your shell's env loading
uvicorn main:app --reload --port 8000
```

Backend will run at `http://localhost:8000`. Check `http://localhost:8000/health`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will run at `http://localhost:5173`.

## Demo script (for hackathon pitch)

1. Click "Obvious phishing" sample → shows High Risk, High confidence,
   explains domain mismatch + urgency + OTP request.
2. Click "Legitimate but urgent" sample → shows Safe, despite urgent language,
   because domain matches and no sensitive info is requested.
3. Click "Ambiguous case" sample → shows Caution, Low/Medium confidence,
   model explicitly says evidence is mixed rather than forcing a verdict.
4. Click "Show raw evidence trail" → demonstrates full auditability/traceability
   of every signal that fed into the decision.

## Project structure

```
phishing-detector/
├── backend/
│   ├── main.py            # FastAPI app + /analyze endpoint
│   ├── rules.py            # Layer 1: rule-based signal extraction
│   ├── llm_reasoning.py    # Layer 2: Claude-based reasoning
│   ├── sample_data.py       # Demo messages
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx          # Main UI
    │   ├── main.jsx
    │   └── index.css
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## Extending this for the full hackathon submission

- Add more brands to `KNOWN_BRAND_DOMAINS` in `rules.py`
- Add SMS/chat message support (the input schema already supports it —
  just add a `channel` field and adjust prompt phrasing per channel)
- Add a "batch analyze" mode for testing many messages against a labeled
  dataset (precision/recall metrics look great in a PPT)
- Add highlighting of the exact suspicious phrases/links within the message
  text in the UI
