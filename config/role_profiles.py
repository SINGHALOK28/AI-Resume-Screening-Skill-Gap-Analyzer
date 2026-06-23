"""Preset role profiles with weighted critical skills."""

ROLE_PROFILES = {
    "Custom (manual)": {},
    "Data Scientist": {
        "python": 2.0,
        "machine learning": 2.0,
        "sql": 1.5,
        "statistics": 1.5,
        "pandas": 1.0,
        "scikit-learn": 1.0,
        "deep learning": 1.0,
    },
    "Frontend Developer": {
        "javascript": 2.0,
        "react": 2.0,
        "html": 1.5,
        "css": 1.5,
        "typescript": 1.5,
        "node.js": 1.0,
    },
    "Backend Developer": {
        "python": 2.0,
        "java": 1.5,
        "sql": 2.0,
        "rest api": 1.5,
        "docker": 1.0,
        "kubernetes": 1.0,
    },
    "DevOps Engineer": {
        "docker": 2.0,
        "kubernetes": 2.0,
        "aws": 1.5,
        "ci/cd": 1.5,
        "terraform": 1.5,
        "linux": 1.0,
    },
    "Full Stack Developer": {
        "javascript": 2.0,
        "react": 1.5,
        "node.js": 1.5,
        "sql": 1.5,
        "python": 1.0,
        "docker": 1.0,
    },
    "ML Engineer": {
        "python": 2.0,
        "pytorch": 2.0,
        "tensorflow": 1.5,
        "machine learning": 2.0,
        "docker": 1.0,
        "kubernetes": 1.0,
    },
    "Product Manager": {
        "product management": 2.0,
        "agile": 1.5,
        "scrum": 1.5,
        "communication": 2.0,
        "stakeholder management": 1.5,
        "data analysis": 1.0,
    },
}


def get_role_profile(name: str) -> dict:
    """Return critical skills dict for a role profile name."""
    return dict(ROLE_PROFILES.get(name, {}))


def list_role_profiles() -> list:
    return list(ROLE_PROFILES.keys())
