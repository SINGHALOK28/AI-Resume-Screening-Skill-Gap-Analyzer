"""Build custom skill database from user input."""

from typing import Set

from embeddings.skill_extractor import SOFT_SKILLS, TECHNICAL_SKILLS
from embeddings.skill_normalizer import normalize_skill


def parse_custom_skills(text: str) -> Set[str]:
    """Parse one-skill-per-line custom skill list."""
    if not text or not text.strip():
        return set()
    skills = set()
    for line in text.strip().split("\n"):
        skill = line.strip()
        if skill:
            skills.add(normalize_skill(skill))
    return skills


def build_skill_database(custom_skills_text: str = "") -> Set[str]:
    """Merge default and custom skill databases."""
    base = TECHNICAL_SKILLS.union(SOFT_SKILLS)
    custom = parse_custom_skills(custom_skills_text)
    return base.union(custom)
