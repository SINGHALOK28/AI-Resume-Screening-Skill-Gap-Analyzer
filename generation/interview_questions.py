"""Generate interview questions from skill gaps."""

from typing import Dict, List


QUESTION_TEMPLATES = {
    "technical": "Can you walk us through a project where you used {skill}? What challenges did you face?",
    "missing": "The role requires {skill}. How would you approach learning it, and do you have related experience?",
    "experience": "You have experience with {skill}. How many years have you worked with it in production?",
    "must_have": "This is a required skill: {skill}. Describe your hands-on experience and a specific outcome you delivered.",
}


def generate_interview_questions(
    missing_skills: List[str],
    resume_skills: List[str],
    must_have_missing: List[str] = None,
    max_questions: int = 8,
) -> List[Dict]:
    """Generate tailored interview questions from gaps and strengths."""
    questions = []
    must_have_missing = must_have_missing or []

    for skill in must_have_missing[:3]:
        questions.append({
            "skill": skill,
            "type": "must_have",
            "question": QUESTION_TEMPLATES["must_have"].format(skill=skill),
            "priority": "high",
        })

    for skill in missing_skills:
        if skill in must_have_missing:
            continue
        questions.append({
            "skill": skill,
            "type": "missing",
            "question": QUESTION_TEMPLATES["missing"].format(skill=skill),
            "priority": "medium",
        })
        if len(questions) >= max_questions:
            break

    for skill in resume_skills[:3]:
        if len(questions) >= max_questions:
            break
        questions.append({
            "skill": skill,
            "type": "technical",
            "question": QUESTION_TEMPLATES["technical"].format(skill=skill),
            "priority": "low",
        })

    return questions[:max_questions]
