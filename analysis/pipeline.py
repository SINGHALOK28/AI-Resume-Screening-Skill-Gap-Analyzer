"""Unified analysis pipeline combining all screening features."""

from typing import Dict, Optional, Set

from analysis.anonymizer import anonymize_resume
from analysis.ats_checker import check_ats_compatibility
from analysis.experience_extractor import compute_experience_fit, extract_experience_profile
from analysis.jd_tier_parser import compute_tier_gaps, parse_jd_tiers
from analysis.score_breakdown import compute_score_breakdown
from analysis.section_parser import extract_skills_by_section, parse_resume_sections
from embeddings.skill_confidence import extract_skills_with_confidence
from embeddings.skill_extractor import extract_skills
from embeddings.skill_normalizer import normalize_skills
from generation.interview_questions import generate_interview_questions
from generation.learning_paths import get_learning_paths
from generation.recommendation_generator import get_recommendation_generator
from generation.resume_rewriter import generate_resume_suggestions
from preprocessing.jd_parser import extract_jd_text
from preprocessing.text_cleaner import clean_text


def run_full_analysis(
    resume_text: str,
    jd_text: str,
    critical_skills: Dict[str, float] = None,
    similarity_engine=None,
    recommendation_generator=None,
    skill_database: Set[str] = None,
    anonymize: bool = False,
    filename: str = "",
    override_resume_skills: list = None,
) -> Dict:
    """
    Run complete resume analysis with all feature modules.

    Returns a rich result dict used by the Streamlit UI.
    """
    analysis_text = resume_text
    anonymized_data = None
    if anonymize:
        anonymized_data = anonymize_resume(resume_text)
        analysis_text = anonymized_data["anonymized_text"]

    jd_processed = clean_text(extract_jd_text(jd_text))
    jd_tiers = parse_jd_tiers(jd_processed, skill_database)

    sections = parse_resume_sections(analysis_text)
    section_skills = extract_skills_by_section(sections, skill_database)

    if override_resume_skills is not None:
        resume_skills = normalize_skills(override_resume_skills)
    else:
        resume_skills = normalize_skills(extract_skills(analysis_text, skill_database))
    jd_skills = jd_tiers["all_jd_skills"]
    must_have = jd_tiers["must_have_skills"]
    nice_to_have = jd_tiers["nice_to_have_skills"]

    missing_must, missing_nice, must_rate, nice_rate = compute_tier_gaps(
        resume_skills, must_have, nice_to_have
    )
    missing_skills = list(dict.fromkeys(missing_must + missing_nice))
    if not missing_skills:
        resume_lower = {s.lower() for s in resume_skills}
        missing_skills = [s for s in jd_skills if s.lower() not in resume_lower]

    experience_profile = extract_experience_profile(analysis_text)
    experience_fit = compute_experience_fit(
        experience_profile["years_experience"],
        jd_tiers["min_years_required"],
    )

    if critical_skills:
        match_score, critical_skills_scores = similarity_engine.compute_weighted_similarity(
            analysis_text, jd_processed, critical_skills
        )
    else:
        match_score = similarity_engine.compute_similarity(analysis_text, jd_processed)
        critical_skills_scores = {}

    semantic_score = similarity_engine.compute_similarity(analysis_text, jd_processed)

    score_breakdown = compute_score_breakdown(
        semantic_score=semantic_score,
        resume_skills=resume_skills,
        jd_skills=jd_skills,
        must_have_skills=must_have,
        nice_to_have_skills=nice_to_have,
        critical_skills_scores=critical_skills_scores,
        experience_fit=experience_fit,
        must_rate=must_rate,
        nice_rate=nice_rate,
    )

    if recommendation_generator is None:
        recommendation_generator = get_recommendation_generator(use_local=False)

    feedback = recommendation_generator.generate_feedback(
        missing_skills, resume_skills, score_breakdown["composite_score"]
    )

    skill_confidence = extract_skills_with_confidence(analysis_text, sections, skill_database)
    interview_questions = generate_interview_questions(
        missing_skills, resume_skills, missing_must
    )
    resume_suggestions = generate_resume_suggestions(
        missing_skills, resume_skills, jd_skills,
        score_breakdown["composite_score"], experience_profile,
    )
    learning_paths = get_learning_paths(missing_skills)
    ats_report = check_ats_compatibility(resume_text, filename)

    return {
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "must_have_skills": must_have,
        "nice_to_have_skills": nice_to_have,
        "missing_skills": missing_skills,
        "missing_must_have": missing_must,
        "missing_nice_to_have": missing_nice,
        "must_have_rate": must_rate,
        "nice_to_have_rate": nice_rate,
        "match_score": match_score,
        "composite_score": score_breakdown["composite_score"],
        "score_breakdown": score_breakdown,
        "critical_skills_scores": critical_skills_scores,
        "experience_profile": experience_profile,
        "experience_fit": experience_fit,
        "sections": sections,
        "section_skills": section_skills,
        "skill_confidence": skill_confidence,
        "feedback": feedback,
        "interview_questions": interview_questions,
        "resume_suggestions": resume_suggestions,
        "learning_paths": learning_paths,
        "ats_report": ats_report,
        "anonymized_data": anonymized_data,
        "raw_resume_text": resume_text,
        "resume_text": resume_text[:1000] if len(resume_text) > 1000 else resume_text,
        "resume_text_length": len(resume_text),
        "filename": filename,
    }
