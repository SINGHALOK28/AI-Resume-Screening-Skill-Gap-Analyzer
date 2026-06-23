"""Skill extraction with confidence scores."""

import re
from typing import Dict, List, Set

from embeddings.skill_extractor import TECHNICAL_SKILLS, SOFT_SKILLS, extract_skills


def _confidence_for_skill(skill: str, text: str, section: str = "full_text") -> Dict:
    """Assign confidence based on how explicitly a skill appears."""
    skill_lower = skill.lower()
    text_lower = text.lower()
    score = 0.5
    source = "inferred"

    # Explicit in skills section
    if section == "skills":
        score = 0.95
        source = "skills_section"
    elif re.search(r"\b" + re.escape(skill_lower) + r"\b", text_lower):
        # Listed with bullet or comma (skills list format)
        if re.search(
            r"(skills?|technologies?|tools?|proficient|expertise)[^.]{0,80}\b"
            + re.escape(skill_lower) + r"\b",
            text_lower,
        ):
            score = 0.9
            source = "skills_list"
        elif re.search(
            r"\b(experience with|proficient in|expert in|knowledge of)\s+"
            + re.escape(skill_lower),
            text_lower,
        ):
            score = 0.85
            source = "experience_context"
        elif re.search(r"\b" + re.escape(skill_lower) + r"\b", text_lower):
            score = 0.7
            source = "mentioned"

    level = "high" if score >= 0.85 else "medium" if score >= 0.7 else "low"
    return {"skill": skill, "confidence": round(score, 2), "level": level, "source": source}


def extract_skills_with_confidence(
    text: str,
    sections: Dict[str, str] = None,
    skill_database: Set[str] = None,
) -> List[Dict]:
    """Extract skills with per-skill confidence scores."""
    if skill_database is None:
        skill_database = TECHNICAL_SKILLS.union(SOFT_SKILLS)

    skills = extract_skills(text, skill_database)
    section_skills: Dict[str, Set[str]] = {}
    if sections:
        from analysis.section_parser import extract_skills_by_section
        section_skills = {k: {s.lower() for s in v} for k, v in extract_skills_by_section(sections, skill_database).items()}

    results = []
    for skill in skills:
        sl = skill.lower()
        section = "full_text"
        for sec, skill_set in section_skills.items():
            if sl in skill_set:
                section = sec
                break
        results.append(_confidence_for_skill(skill, text, section))

    return sorted(results, key=lambda x: -x["confidence"])
