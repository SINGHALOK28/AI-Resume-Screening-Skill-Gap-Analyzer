"""Anonymize resume text for bias-reduced screening."""

import re
from typing import Dict


def anonymize_resume(text: str) -> Dict:
    """Remove PII and bias-prone signals from resume text."""
    anonymized = text

    # Email
    anonymized = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[EMAIL]", anonymized)
    # Phone
    anonymized = re.sub(r"\+?\d[\d\s\-().]{8,}\d", "[PHONE]", anonymized)
    # URLs / LinkedIn
    anonymized = re.sub(r"https?://\S+", "[URL]", anonymized)
    anonymized = re.sub(r"linkedin\.com/\S+", "[LINKEDIN]", anonymized, flags=re.IGNORECASE)
    # Common name line at top (first non-empty line often name)
    lines = anonymized.split("\n")
    if lines and len(lines[0].split()) <= 4 and not any(c.isdigit() for c in lines[0]):
        lines[0] = "[CANDIDATE NAME]"
        anonymized = "\n".join(lines)

    removed_items = {
        "emails_removed": len(re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", text)),
        "phones_removed": len(re.findall(r"\+?\d[\d\s\-().]{8,}\d", text)),
        "urls_removed": len(re.findall(r"https?://\S+", text)),
    }

    return {
        "anonymized_text": anonymized,
        "removed_items": removed_items,
        "original_length": len(text),
        "anonymized_length": len(anonymized),
    }
