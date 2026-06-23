"""Skill synonym normalization."""

from typing import Dict, List, Set

SKILL_SYNONYMS: Dict[str, str] = {
    "react.js": "react",
    "reactjs": "react",
    "react js": "react",
    "node": "node.js",
    "nodejs": "node.js",
    "vue.js": "vue",
    "vuejs": "vue",
    "angular.js": "angular",
    "angularjs": "angular",
    "next.js": "next.js",
    "nextjs": "next.js",
    "express.js": "express",
    "expressjs": "express",
    "postgres": "postgresql",
    "postgre": "postgresql",
    "mongo": "mongodb",
    "k8s": "kubernetes",
    "amazon web services": "aws",
    "google cloud": "gcp",
    "google cloud platform": "gcp",
    "microsoft azure": "azure",
    "ml": "machine learning",
    "ai": "machine learning",
    "deep-learning": "deep learning",
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "py torch": "pytorch",
    "tensorflow 2": "tensorflow",
    "c sharp": "c#",
    "c plus plus": "c++",
    "js": "javascript",
    "ts": "typescript",
    "html5": "html",
    "css3": "css",
    "ci cd": "ci/cd",
    "cicd": "ci/cd",
    "restful api": "rest api",
    "rest apis": "rest api",
    "agile methodology": "agile",
}


def normalize_skill(skill: str) -> str:
    """Map a skill variant to its canonical form."""
    key = skill.lower().strip()
    return SKILL_SYNONYMS.get(key, key)


def normalize_skills(skills: List[str]) -> List[str]:
    """Normalize and deduplicate a skill list preserving order."""
    seen: Set[str] = set()
    result: List[str] = []
    for skill in skills:
        canonical = normalize_skill(skill)
        if canonical not in seen:
            seen.add(canonical)
            result.append(canonical)
    return result


def expand_skill_database(extra_skills: Set[str] = None) -> Set[str]:
    """Build a skill database including synonyms pointing to canonical skills."""
    from embeddings.skill_extractor import TECHNICAL_SKILLS, SOFT_SKILLS

    base = TECHNICAL_SKILLS.union(SOFT_SKILLS)
    if extra_skills:
        base = base.union({s.lower() for s in extra_skills})
    return base
