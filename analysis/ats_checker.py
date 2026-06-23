"""ATS compatibility analysis."""

import re
from typing import Dict, List


def check_ats_compatibility(text: str, filename: str = "") -> Dict:
    """Check resume for common ATS parsing issues."""
    issues: List[Dict] = []
    score = 100

    if not text or len(text.strip()) < 50:
        issues.append({"severity": "high", "message": "Very little text extracted — ATS may not parse this resume."})
        score -= 40

    if len(text) < 200:
        issues.append({"severity": "medium", "message": "Short resume text — may be image-based or poorly formatted."})
        score -= 15

    # Tables and columns (heuristic)
    if text.count("|") > 10 or text.count("\t") > 15:
        issues.append({"severity": "medium", "message": "Heavy use of tables/columns may confuse ATS parsers."})
        score -= 10

    # Special characters
    special_ratio = len(re.findall(r"[^\w\s.,;:\-@#+/()&'\"]", text)) / max(len(text), 1)
    if special_ratio > 0.05:
        issues.append({"severity": "low", "message": "Unusual special characters detected."})
        score -= 5

    # Missing common sections
    text_lower = text.lower()
    if "experience" not in text_lower and "work" not in text_lower:
        issues.append({"severity": "medium", "message": "No clear Experience section found."})
        score -= 10
    if "education" not in text_lower and "degree" not in text_lower and "university" not in text_lower:
        issues.append({"severity": "low", "message": "No clear Education section found."})
        score -= 5
    if "skill" not in text_lower and len(re.findall(r"\b(python|java|sql|javascript)\b", text_lower)) < 2:
        issues.append({"severity": "medium", "message": "Skills section or technical keywords may be missing."})
        score -= 10

    # Contact info patterns
    has_email = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text))
    has_phone = bool(re.search(r"\+?\d[\d\s\-().]{8,}\d", text))
    if not has_email:
        issues.append({"severity": "low", "message": "No email address detected."})
        score -= 3
    if not has_phone:
        issues.append({"severity": "low", "message": "No phone number detected."})
        score -= 2

    # File format note
    if filename.lower().endswith(".doc"):
        issues.append({"severity": "low", "message": "Legacy .doc format — PDF or DOCX is preferred for ATS."})
        score -= 5

    score = max(0, min(100, score))
    rating = "Excellent" if score >= 85 else "Good" if score >= 70 else "Fair" if score >= 50 else "Poor"

    return {
        "ats_score": score,
        "rating": rating,
        "issues": issues,
        "has_email": has_email,
        "has_phone": has_phone,
    }
