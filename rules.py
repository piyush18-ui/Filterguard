"""
Layer 1: Rule-based signal extraction.

This module inspects a message (sender, subject, body) and extracts a
structured "evidence bundle" of deterministic, explainable signals.
No ML/LLM here on purpose — this layer must be fast, auditable, and
100% reproducible so its output can be trusted as ground evidence for
the reasoning layer (llm_reasoning.py).
"""

import re
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Reference data — extend these lists as you find more real-world patterns.
# ---------------------------------------------------------------------------

KNOWN_BRAND_DOMAINS = {
    "sbi": ["onlinesbi.sbi", "sbi.co.in"],
    "paypal": ["paypal.com"],
    "amazon": ["amazon.com", "amazon.in"],
    "google": ["google.com", "accounts.google.com"],
    "microsoft": ["microsoft.com", "office.com", "live.com"],
    "hdfc": ["hdfcbank.com"],
    "icici": ["icicibank.com"],
}

URGENCY_PHRASES = [
    "act now", "act immediately", "immediately", "urgent", "urgently",
    "account will be suspended", "account suspended", "within 24 hours",
    "within 12 hours", "verify now", "verify immediately", "final notice",
    "expire", "expires today", "limited time", "act fast",
]

THREAT_PHRASES = [
    "legal action", "account will be closed", "unauthorized access",
    "suspicious activity detected", "your account has been compromised",
    "failure to comply", "penalty", "blocked permanently",
]

REWARD_PHRASES = [
    "you've won", "you have won", "claim your prize", "refund pending",
    "cashback waiting", "congratulations", "lucky winner", "free gift",
]

SENSITIVE_INFO_KEYWORDS = [
    "password", "otp", "one time password", "cvv", "card number",
    "pin number", "aadhaar", "social security", "bank account number",
    "login credentials", "security code",
]

GENERIC_GREETINGS = [
    "dear customer", "dear user", "dear valued customer",
    "dear account holder", "dear sir/madam", "hello user",
]

URL_SHORTENERS = [
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd", "buff.ly",
]

CONFIDENTIALITY_PRESSURE = [
    "don't tell", "do not tell", "keep this confidential",
    "between us", "don't inform", "do not inform your",
]

SUSPICIOUS_ATTACHMENT_EXTENSIONS = [".exe", ".scr", ".bat", ".js", ".vbs", ".jar"]


def _contains_any(text: str, phrases: list[str]) -> list[str]:
    text_lower = text.lower()
    return [p for p in phrases if p in text_lower]


def _extract_urls(text: str) -> list[str]:
    url_pattern = r"https?://[^\s<>\"')]+|www\.[^\s<>\"')]+"
    return re.findall(url_pattern, text, flags=re.IGNORECASE)


def _domain_of(url: str) -> str:
    if not url.startswith("http"):
        url = "http://" + url
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def check_sender_domain(sender_email: str, claimed_brand: str | None) -> dict:
    """Compare sender domain against known domains for a claimed brand."""
    if not sender_email or "@" not in sender_email:
        return {"checked": False, "mismatch": False, "reason": "no sender email provided"}

    domain = sender_email.split("@")[-1].lower()

    if not claimed_brand:
        return {"checked": False, "mismatch": False, "reason": "no claimed brand detected"}

    brand_key = claimed_brand.lower()
    known_domains = KNOWN_BRAND_DOMAINS.get(brand_key)

    if not known_domains:
        return {"checked": False, "mismatch": False, "reason": f"'{claimed_brand}' not in known-brand list"}

    mismatch = not any(domain == d or domain.endswith("." + d) for d in known_domains)
    return {
        "checked": True,
        "mismatch": mismatch,
        "sender_domain": domain,
        "expected_domains": known_domains,
    }


def check_urls(text: str) -> dict:
    urls = _extract_urls(text)
    findings = []
    for url in urls:
        domain = _domain_of(url)
        is_shortener = any(s in domain for s in URL_SHORTENERS)
        is_ip = bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}", domain))
        subdomain_count = domain.count(".") - 1  # rough heuristic
        findings.append({
            "url": url,
            "domain": domain,
            "is_shortener": is_shortener,
            "is_raw_ip": is_ip,
            "excessive_subdomains": subdomain_count >= 3,
        })
    return {
        "url_count": len(urls),
        "urls": findings,
        "any_shortener": any(f["is_shortener"] for f in findings),
        "any_raw_ip": any(f["is_raw_ip"] for f in findings),
    }


def check_language_signals(text: str) -> dict:
    return {
        "urgency_phrases_found": _contains_any(text, URGENCY_PHRASES),
        "threat_phrases_found": _contains_any(text, THREAT_PHRASES),
        "reward_phrases_found": _contains_any(text, REWARD_PHRASES),
        "sensitive_info_requested": _contains_any(text, SENSITIVE_INFO_KEYWORDS),
        "generic_greeting": _contains_any(text, GENERIC_GREETINGS),
        "confidentiality_pressure": _contains_any(text, CONFIDENTIALITY_PRESSURE),
    }


def check_attachment(filename: str | None) -> dict:
    if not filename:
        return {"checked": False, "suspicious": False}
    suspicious = any(filename.lower().endswith(ext) for ext in SUSPICIOUS_ATTACHMENT_EXTENSIONS)
    return {"checked": True, "filename": filename, "suspicious": suspicious}


def detect_claimed_brand(text: str) -> str | None:
    """Very simple heuristic: look for a known brand name mentioned in the text."""
    text_lower = text.lower()
    for brand in KNOWN_BRAND_DOMAINS:
        if brand in text_lower:
            return brand
    return None


def extract_evidence(
    subject: str = "",
    body: str = "",
    sender_email: str = "",
    attachment_filename: str | None = None,
) -> dict:
    """
    Main entry point: run all rule checks and return a structured
    evidence bundle. This bundle is what gets handed to the LLM
    reasoning layer.
    """
    full_text = f"{subject}\n{body}"
    claimed_brand = detect_claimed_brand(full_text)

    evidence = {
        "claimed_brand": claimed_brand,
        "sender_domain_check": check_sender_domain(sender_email, claimed_brand),
        "url_check": check_urls(full_text),
        "language_signals": check_language_signals(full_text),
        "attachment_check": check_attachment(attachment_filename),
    }
    return evidence
