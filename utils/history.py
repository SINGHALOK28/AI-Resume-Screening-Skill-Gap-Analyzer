"""Analysis history management for Streamlit session."""

import json
from datetime import datetime
from typing import Dict, List


def add_to_history(session_state, result: Dict, candidate_name: str = "", mode: str = "single"):
    """Append an analysis result to session history."""
    if "analysis_history" not in session_state:
        session_state["analysis_history"] = []

    entry = {
        "timestamp": datetime.now().isoformat(),
        "candidate_name": candidate_name or result.get("filename", "Unknown"),
        "mode": mode,
        "match_score": result.get("match_score", 0),
        "composite_score": result.get("score_breakdown", {}).get("composite_score", result.get("match_score", 0)),
        "resume_skills_count": len(result.get("resume_skills", [])),
        "missing_skills_count": len(result.get("missing_skills", [])),
        "must_have_missing": len(result.get("missing_must_have", [])),
        "ats_score": result.get("ats_report", {}).get("ats_score"),
        "filename": result.get("filename", ""),
    }
    session_state["analysis_history"].insert(0, entry)
    session_state["analysis_history"] = session_state["analysis_history"][:50]


def get_history(session_state) -> List[Dict]:
    return session_state.get("analysis_history", [])


def history_to_json(session_state) -> str:
    return json.dumps(get_history(session_state), indent=2)
