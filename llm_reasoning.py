"""
Layer 2: LLM reasoning over extracted evidence.

Takes the deterministic evidence bundle from rules.py and asks Claude
to reason over it like a human security analyst would — weighing
combinations of signals rather than triggering on any single one,
and producing a structured, explainable verdict.
"""

import json
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a cybersecurity analyst assistant that evaluates potential phishing
or social engineering attempts. You will be given a message and a set of
extracted rule-based signals. Your job is to:

1. Assess the overall deception risk: "Safe", "Caution", or "High Risk"
2. Provide a confidence level: "Low", "Medium", or "High"
3. List the top 3 factors contributing to your assessment, in plain language
   a normal user can understand (no jargon)
4. If risk is "Caution" or "High Risk", suggest one clear, practical action
   the user should take
5. If information is ambiguous or insufficient, say so explicitly in your
   reasoning_summary rather than forcing a confident conclusion

Important judgment rules:
- Do NOT treat urgency alone as proof of phishing — many legitimate messages
  (invoice reminders, deadline notices) are urgent. Consider the COMBINATION
  of signals, not any single one in isolation.
- A domain mismatch against a claimed brand is a strong signal.
- Multiple weak signals stacking together (urgency + sensitive info request +
  shortened URL) is stronger evidence than any single moderate signal.
- Be conservative about false positives on legitimate business communication.
- If the sender/brand could not be matched against known domains, treat that
  as unknown rather than automatically suspicious — say so in your reasoning.

Respond ONLY with valid JSON in this exact format, nothing else:
{
  "risk_level": "Safe | Caution | High Risk",
  "confidence": "Low | Medium | High",
  "top_factors": ["...", "...", "..."],
  "recommended_action": "...",
  "reasoning_summary": "..."
}
"""


def assess_message(message_text: str, evidence: dict) -> dict:
    """
    Calls Claude with the message + rule-based evidence bundle and
    returns a structured risk assessment dict.
    """
    user_prompt = f"""MESSAGE:
{message_text}

EXTRACTED SIGNALS (from deterministic rule checks):
{json.dumps(evidence, indent=2)}
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw_text = "".join(
        block.text for block in response.content if block.type == "text"
    ).strip()

    # Defensive parsing: strip markdown code fences if the model adds them
    cleaned = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback so the API never hard-fails the request
        result = {
            "risk_level": "Caution",
            "confidence": "Low",
            "top_factors": ["Could not parse model output cleanly"],
            "recommended_action": "Manually review this message.",
            "reasoning_summary": f"Model returned unparseable output: {raw_text[:300]}",
        }

    return result
