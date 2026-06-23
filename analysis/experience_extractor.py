"""Extract experience, education, and certifications from resume text."""

import re
from typing import Dict, List

EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "ph.d", "mba", "b.s", "b.a", "m.s", "m.a",
    "degree", "university", "college", "diploma", "certification", "certified",
]
CERT_KEYWORDS = [
    "certified", "certification", "aws certified", "pmp", "cissp", "comptia",
    "google cloud", "azure certified", "scrum master", "cisco",
]


def _parse_years_from_text(text: str) -> float:
    """Estimate total years of experience from resume text."""
    patterns = [
        r"(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience|exp)",
        r"(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?\w+",
        r"experience[:\s]+(\d+)\+?\s*(?:years?|yrs?)",
        r"(\d+)\+?\s*(?:years?|yrs?)\s+in\s+",
    ]
    years_found = []
    for pattern in patterns:
        for match in re.finditer(pattern, text.lower()):
            years_found.append(int(match.group(1)))

    if years_found:
        return float(max(years_found))

    # Estimate from date ranges like 2018 - 2023 or 2018–Present
    date_ranges = re.findall(
        r"(20\d{2}|19\d{2})\s*[-–—to]+\s*(20\d{2}|present|current|now)",
        text.lower(),
    )
    total = 0.0
    for start, end in date_ranges:
        start_y = int(start)
        end_y = 2026 if end in ("present", "current", "now") else int(end)
        if end_y >= start_y:
            total += end_y - start_y
    return min(total, 40.0) if total > 0 else 0.0


def _extract_job_titles(text: str) -> List[str]:
    """Extract likely job titles from experience section."""
    titles = []
    title_patterns = [
        r"(?:^|\n)\s*([A-Z][A-Za-z\s/&]+(?:Engineer|Developer|Manager|Analyst|Architect|Lead|Director|Consultant|Designer|Scientist|Intern))\s*(?:\n|at|@|,|\|)",
    ]
    for pattern in title_patterns:
        for match in re.finditer(pattern, text):
            title = match.group(1).strip()
            if 3 < len(title) < 60:
                titles.append(title)
    return titles[:10]


def _extract_education(text: str) -> List[str]:
    """Extract education lines from resume."""
    education = []
    lines = text.split("\n")
    in_edu = False
    for line in lines:
        line_lower = line.lower().strip()
        if any(kw in line_lower for kw in ["education", "academic", "qualification"]):
            in_edu = True
            continue
        if in_edu and line.strip():
            if any(kw in line_lower for kw in EDUCATION_KEYWORDS):
                education.append(line.strip())
            elif re.match(r"^[A-Z]", line.strip()) and len(line.strip()) < 5:
                in_edu = False
        elif any(kw in line_lower for kw in EDUCATION_KEYWORDS) and len(line.strip()) > 10:
            education.append(line.strip())
    return education[:5]


def _extract_certifications(text: str) -> List[str]:
    """Extract certification mentions."""
    certs = []
    for line in text.split("\n"):
        line_lower = line.lower()
        if any(kw in line_lower for kw in CERT_KEYWORDS) and len(line.strip()) > 5:
            certs.append(line.strip())
    return certs[:8]


def extract_experience_profile(text: str) -> Dict:
    """Build experience and education profile from resume text."""
    years = _parse_years_from_text(text)
    return {
        "years_experience": years,
        "job_titles": _extract_job_titles(text),
        "education": _extract_education(text),
        "certifications": _extract_certifications(text),
    }


def compute_experience_fit(years: float, min_required: int) -> Dict:
    """Compare candidate experience against JD requirement."""
    if min_required <= 0:
        return {"meets_requirement": True, "gap_years": 0, "fit_score": 1.0}
    meets = years >= min_required
    gap = max(0, min_required - years)
    fit = min(1.0, years / min_required) if min_required else 1.0
    return {
        "meets_requirement": meets,
        "gap_years": gap,
        "fit_score": round(fit, 2),
        "candidate_years": years,
        "required_years": min_required,
    }
