"""Explainable scoring breakdown."""

from typing import Dict, List


def compute_score_breakdown(
    semantic_score: float,
    resume_skills: List[str],
    jd_skills: List[str],
    must_have_skills: List[str],
    nice_to_have_skills: List[str],
    critical_skills_scores: Dict[str, float],
    experience_fit: Dict,
    must_rate: float,
    nice_rate: float,
) -> Dict:
    """Build a transparent score breakdown for recruiters."""
    resume_lower = {s.lower() for s in resume_skills}
    jd_lower = {s.lower() for s in jd_skills}

    overlap = [s for s in jd_skills if s.lower() in resume_lower]
    skill_overlap_rate = len(overlap) / len(jd_skills) if jd_skills else 0.0

    critical_rate = 0.0
    if critical_skills_scores:
        total = sum(critical_skills_scores.values())
        max_possible = len(critical_skills_scores)
        critical_rate = total / max_possible if max_possible else 0.0

    exp_score = experience_fit.get("fit_score", 1.0)

    # Weighted composite (must-have weighted highest)
    composite = (
        semantic_score * 0.25
        + skill_overlap_rate * 0.20
        + must_rate * 0.25
        + nice_rate * 0.10
        + critical_rate * 0.10
        + exp_score * 0.10
    )
    composite = min(1.0, max(0.0, composite))

    return {
        "composite_score": round(composite, 4),
        "components": {
            "semantic_similarity": {"score": round(semantic_score, 4), "weight": "25%"},
            "skill_overlap": {
                "score": round(skill_overlap_rate, 4),
                "weight": "20%",
                "matched": len(overlap),
                "total_jd_skills": len(jd_skills),
            },
            "must_have_match": {"score": round(must_rate, 4), "weight": "25%"},
            "nice_to_have_match": {"score": round(nice_rate, 4), "weight": "10%"},
            "critical_skills": {"score": round(critical_rate, 4), "weight": "10%"},
            "experience_fit": {"score": round(exp_score, 4), "weight": "10%"},
        },
        "overlapping_skills": overlap[:30],
        "experience_fit": experience_fit,
    }
