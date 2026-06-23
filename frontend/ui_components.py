"""Streamlit UI components for enhanced analysis display."""

import pandas as pd
import streamlit as st

from embeddings.skill_extractor import categorize_skills


def render_score_breakdown(score_breakdown: dict):
    """Display explainable scoring breakdown."""
    st.subheader("📈 Score Breakdown")
    components = score_breakdown.get("components", {})
    cols = st.columns(3)
    labels = [
        ("semantic_similarity", "Semantic"),
        ("skill_overlap", "Skill Overlap"),
        ("must_have_match", "Must-Have"),
        ("nice_to_have_match", "Nice-to-Have"),
        ("critical_skills", "Critical Skills"),
        ("experience_fit", "Experience"),
    ]
    for i, (key, label) in enumerate(labels):
        comp = components.get(key, {})
        with cols[i % 3]:
            st.metric(label, f"{comp.get('score', 0):.0%}", help=f"Weight: {comp.get('weight', '')}")

    exp = score_breakdown.get("experience_fit", {})
    if exp.get("required_years", 0) > 0:
        status = "Meets requirement" if exp.get("meets_requirement") else f"Gap: {exp.get('gap_years', 0)} yrs"
        st.caption(
            f"Experience: {exp.get('candidate_years', 0):.0f} yrs "
            f"(required: {exp.get('required_years', 0)}) — {status}"
        )


def render_jd_tiers(results: dict):
    """Display must-have vs nice-to-have analysis."""
    must = results.get("must_have_skills", [])
    nice = results.get("nice_to_have_skills", [])
    if not must and not nice:
        return
    st.subheader("🎯 JD Skill Tiers")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Must-Have**")
        if must:
            st.write(", ".join(must[:20]))
        else:
            st.caption("None detected — paste JD with 'Required' / 'Must have' sections for better tiering.")
        missing_must = results.get("missing_must_have", [])
        if missing_must:
            st.error(f"Missing must-have: {', '.join(missing_must[:10])}")
    with c2:
        st.markdown("**Nice-to-Have**")
        if nice:
            st.write(", ".join(nice[:20]))
        missing_nice = results.get("missing_nice_to_have", [])
        if missing_nice:
            st.warning(f"Missing nice-to-have: {', '.join(missing_nice[:10])}")


def render_experience(results: dict):
    """Display experience and education profile."""
    profile = results.get("experience_profile", {})
    if not profile:
        return
    st.subheader("👔 Experience & Education")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Years Experience", f"{profile.get('years_experience', 0):.0f}")
    with c2:
        st.metric("Education Entries", len(profile.get("education", [])))
    with c3:
        st.metric("Certifications", len(profile.get("certifications", [])))
    if profile.get("job_titles"):
        st.write("**Titles:**", ", ".join(profile["job_titles"][:5]))
    if profile.get("education"):
        for edu in profile["education"][:3]:
            st.write(f"• {edu}")
    if profile.get("certifications"):
        for cert in profile["certifications"][:3]:
            st.write(f"• {cert}")


def render_skill_confidence(skill_confidence: list):
    """Display skill confidence table."""
    if not skill_confidence:
        return
    st.subheader("🔬 Skill Confidence")
    df = pd.DataFrame(skill_confidence[:25])
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_sections(section_skills: dict):
    """Display skills by resume section."""
    if not section_skills:
        return
    st.subheader("📑 Skills by Section")
    for section, skills in section_skills.items():
        st.write(f"**{section.replace('_', ' ').title()}:** {', '.join(skills[:15])}")


def render_ats_report(ats_report: dict):
    """Display ATS compatibility report."""
    if not ats_report:
        return
    st.subheader("🤖 ATS Compatibility")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("ATS Score", f"{ats_report.get('ats_score', 0)}/100")
    with c2:
        st.metric("Rating", ats_report.get("rating", "N/A"))
    for issue in ats_report.get("issues", []):
        icon = "🔴" if issue["severity"] == "high" else "🟡" if issue["severity"] == "medium" else "🔵"
        st.write(f"{icon} {issue['message']}")


def render_interview_questions(questions: list):
    """Display generated interview questions."""
    if not questions:
        return
    st.subheader("🎤 Interview Questions")
    for q in questions:
        priority = q.get("priority", "medium")
        icon = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
        st.write(f"{icon} **{q.get('skill', '')}:** {q.get('question', '')}")


def render_resume_suggestions(suggestions: list):
    """Display resume rewrite suggestions."""
    if not suggestions:
        return
    st.subheader("✏️ Resume Improvement Suggestions")
    for s in suggestions:
        st.write(f"**[{s.get('category', '')}]** {s.get('suggestion', '')}")


def render_learning_paths(paths: list):
    """Display learning path recommendations."""
    if not paths:
        return
    st.subheader("📚 Learning Paths")
    for item in paths:
        st.markdown(f"**{item['skill']}**")
        for res in item.get("resources", []):
            st.markdown(f"- [{res['title']}]({res['url']}) ({res['type']})")


def render_charts(results: dict, group_results: list = None):
    """Visual analytics charts."""
    st.subheader("📊 Visual Analytics")
    if group_results:
        df = pd.DataFrame([
            {"Candidate": r.get("filename", f"Resume {i+1}"), "Score": r.get("composite_score", r.get("match_score", 0))}
            for i, r in enumerate(group_results)
        ])
        st.bar_chart(df.set_index("Candidate")["Score"])
        return

    breakdown = results.get("score_breakdown", {}).get("components", {})
    if breakdown:
        chart_data = pd.DataFrame({
            "Component": [k.replace("_", " ").title() for k in breakdown.keys()],
            "Score": [v.get("score", 0) for v in breakdown.values()],
        })
        st.bar_chart(chart_data.set_index("Component")["Score"])

    categorized = categorize_skills(results.get("resume_skills", []))
    if categorized:
        cat_df = pd.DataFrame({
            "Category": [k.replace("_", " ").title() for k in categorized.keys()],
            "Count": [len(v) for v in categorized.values()],
        })
        st.caption("Skills by category")
        st.bar_chart(cat_df.set_index("Category")["Count"])


def render_history(history: list):
    """Display analysis history."""
    if not history:
        st.info("No analysis history yet.")
        return
    st.subheader("🕐 Analysis History")
    st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)
