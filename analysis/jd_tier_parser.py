"""Parse job description into must-have vs nice-to-have skill tiers."""

import re
from typing import Dict, List, Tuple

from embeddings.skill_extractor import extract_skills
from embeddings.skill_normalizer import normalize_skills

MUST_HAVE_KEYWORDS = [
    "must have", "must-have", "required", "requirements", "mandatory",
    "essential", "need to have", "minimum qualifications", "minimum requirements",
]
NICE_TO_HAVE_KEYWORDS = [
    "nice to have", "nice-to-have", "preferred", "bonus", "plus",
    "desirable", "optional", "a plus", "would be a plus", "advantage",
]


def _split_jd_sections(jd_text: str) -> Dict[str, str]:
    """Split JD into tier sections based on heading keywords."""
    sections = {"must_have": "", "nice_to_have": "", "general": jd_text}
    lines = jd_text.split("\n")
    current = "general"

    for line in lines:
        line_lower = line.lower().strip()
        if any(kw in line_lower for kw in MUST_HAVE_KEYWORDS):
            current = "must_have"
            remainder = re.sub(r"^.*?(must have|required|mandatory|essential)[:\s]*", "", line_lower, count=1)
            if remainder.strip():
                sections[current] += remainder + "\n"
            continue
        if any(kw in line_lower for kw in NICE_TO_HAVE_KEYWORDS):
            current = "nice_to_have"
            remainder = re.sub(r"^.*?(nice to have|preferred|bonus|optional|desirable)[:\s]*", "", line_lower, count=1)
            if remainder.strip():
                sections[current] += remainder + "\n"
            continue
        sections[current] += line + "\n"

    return sections


def _extract_years_requirement(text: str) -> int:
    """Extract minimum years of experience mentioned in JD."""
    patterns = [
        r"(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience",
        r"minimum\s+of\s+(\d+)\s+(?:years?|yrs?)",
        r"at\s+least\s+(\d+)\s+(?:years?|yrs?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return int(match.group(1))
    return 0


def parse_jd_tiers(jd_text: str, skill_database=None) -> Dict:
    """
    Parse JD into must-have and nice-to-have skills.

    Returns dict with must_have_skills, nice_to_have_skills, all_jd_skills,
    min_years_required, and section texts.
    """
    if not jd_text:
        return {
            "must_have_skills": [],
            "nice_to_have_skills": [],
            "all_jd_skills": [],
            "min_years_required": 0,
            "sections": {},
        }

    sections = _split_jd_sections(jd_text)
    must_have = normalize_skills(extract_skills(sections["must_have"], skill_database))
    nice_to_have = normalize_skills(extract_skills(sections["nice_to_have"], skill_database))
    all_skills = normalize_skills(extract_skills(jd_text, skill_database))

    # Skills only in general section default to must-have if not in nice-to-have
    general_skills = normalize_skills(extract_skills(sections["general"], skill_database))
    must_set = {s.lower() for s in must_have}
    nice_set = {s.lower() for s in nice_to_have}

    for skill in general_skills:
        sl = skill.lower()
        if sl not in must_set and sl not in nice_set:
            must_have.append(skill)
            must_set.add(sl)

    # Remove nice-to-have duplicates from must-have
    must_have = [s for s in must_have if s.lower() not in nice_set]
    nice_to_have = [s for s in nice_to_have if s.lower() not in must_set]

    # If no tier split detected, treat all JD skills as must-have
    if not must_have and not nice_to_have and all_skills:
        must_have = list(all_skills)

    return {
        "must_have_skills": must_have,
        "nice_to_have_skills": nice_to_have,
        "all_jd_skills": all_skills,
        "min_years_required": _extract_years_requirement(jd_text),
        "sections": sections,
    }


def compute_tier_gaps(
    resume_skills: List[str],
    must_have: List[str],
    nice_to_have: List[str],
) -> Tuple[List[str], List[str], float, float]:
    """Return missing skills and tier match rates."""
    resume_lower = {s.lower() for s in resume_skills}

    missing_must = [s for s in must_have if s.lower() not in resume_lower]
    missing_nice = [s for s in nice_to_have if s.lower() not in resume_lower]

    must_rate = (
        (len(must_have) - len(missing_must)) / len(must_have) if must_have else 1.0
    )
    nice_rate = (
        (len(nice_to_have) - len(missing_nice)) / len(nice_to_have) if nice_to_have else 1.0
    )
    return missing_must, missing_nice, must_rate, nice_rate
