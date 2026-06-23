"""Helper to load JD text from paste or file upload."""

from preprocessing.resume_parser import extract_resume_text


def load_jd_text(jd_text: str = "", jd_file=None) -> str:
    """Combine JD from pasted text and/or uploaded file."""
    parts = []
    if jd_text and jd_text.strip():
        parts.append(jd_text.strip())
    if jd_file is not None:
        extracted = extract_resume_text(jd_file)
        if extracted:
            parts.append(extracted)
    return "\n\n".join(parts)
