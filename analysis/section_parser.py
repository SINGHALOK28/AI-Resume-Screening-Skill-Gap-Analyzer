"""Section-aware resume parsing."""

import re
from typing import Dict, List

SECTION_HEADERS = {
    "experience": [
        "experience", "work experience", "professional experience",
        "employment", "work history", "career",
    ],
    "education": ["education", "academic", "qualifications", "degrees"],
    "skills": ["skills", "technical skills", "core competencies", "technologies", "expertise"],
    "projects": ["projects", "personal projects", "key projects"],
    "summary": ["summary", "profile", "objective", "about me"],
    "certifications": ["certifications", "certificates", "licenses"],
}


def parse_resume_sections(text: str) -> Dict[str, str]:
    """Split resume text into named sections."""
    sections = {key: "" for key in SECTION_HEADERS}
    sections["full_text"] = text

    if not text:
        return sections

    lines = text.split("\n")
    current = "summary"
    buffer: List[str] = []

    def flush():
        nonlocal buffer
        if buffer:
            sections[current] = (sections[current] + "\n" + "\n".join(buffer)).strip()
            buffer = []

    for line in lines:
        line_stripped = line.strip()
        line_lower = line_stripped.lower()
        matched = False
        for section, headers in SECTION_HEADERS.items():
            if any(
                line_lower == h or line_lower.startswith(h + ":") or line_lower.startswith(h + " ")
                for h in headers
            ):
                flush()
                current = section
                matched = True
                break
        if not matched and line_stripped:
            buffer.append(line_stripped)

    flush()
    return {k: v for k, v in sections.items() if v}


def extract_skills_by_section(sections: Dict[str, str], skill_database=None) -> Dict[str, List[str]]:
    """Extract skills from each resume section."""
    from embeddings.skill_extractor import extract_skills
    from embeddings.skill_normalizer import normalize_skills

    result = {}
    for section, content in sections.items():
        if section == "full_text" or not content:
            continue
        skills = normalize_skills(extract_skills(content, skill_database))
        if skills:
            result[section] = skills
    return result
