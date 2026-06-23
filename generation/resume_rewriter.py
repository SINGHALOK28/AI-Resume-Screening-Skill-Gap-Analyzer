"""Resume rewrite suggestions aligned to job description."""

from typing import Dict, List


def generate_resume_suggestions(
    missing_skills: List[str],
    resume_skills: List[str],
    jd_skills: List[str],
    match_score: float,
    experience_profile: Dict = None,
) -> List[Dict]:
    """Suggest concrete resume improvements."""
    suggestions = []
    experience_profile = experience_profile or {}

    if missing_skills:
        top_missing = missing_skills[:5]
        suggestions.append({
            "category": "Skills",
            "suggestion": f"Add a dedicated Skills section highlighting: {', '.join(top_missing)}. "
            "If you have related experience, mention it explicitly.",
            "priority": "high",
        })

    if match_score < 0.5:
        suggestions.append({
            "category": "Keywords",
            "suggestion": "Mirror key phrases from the job description in your summary and experience bullets. "
            "Use the same terminology the employer uses.",
            "priority": "high",
        })

    if experience_profile.get("years_experience", 0) < 2:
        suggestions.append({
            "category": "Experience",
            "suggestion": "Expand project descriptions with quantified outcomes (e.g., 'Reduced latency by 30%').",
            "priority": "medium",
        })

    overlap = [s for s in resume_skills if s.lower() in {j.lower() for j in jd_skills}]
    if overlap:
        suggestions.append({
            "category": "Strengths",
            "suggestion": f"Lead with your matching strengths: {', '.join(overlap[:5])}. "
            "Move relevant experience to the top of your resume.",
            "priority": "medium",
        })

    suggestions.append({
        "category": "Format",
        "suggestion": "Use bullet points starting with action verbs (Built, Led, Optimized). "
        "Keep each bullet to 1–2 lines for ATS readability.",
        "priority": "low",
    })

    if not experience_profile.get("certifications"):
        suggestions.append({
            "category": "Certifications",
            "suggestion": "Consider adding relevant certifications if you have them — they strengthen credibility for technical roles.",
            "priority": "low",
        })

    return suggestions
