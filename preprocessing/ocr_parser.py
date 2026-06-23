"""OCR fallback for scanned/image-based PDFs."""

import io
from typing import Optional


def extract_text_with_ocr(file_bytes: bytes) -> Optional[str]:
    """
    Extract text from image-based PDF using OCR.
    Requires pytesseract and Tesseract OCR installed on the system.
    """
    try:
        import pytesseract
        from pdf2image import convert_from_bytes
    except ImportError:
        return None

    try:
        images = convert_from_bytes(file_bytes, dpi=200)
        parts = []
        for image in images[:10]:  # Limit pages for performance
            text = pytesseract.image_to_string(image)
            if text.strip():
                parts.append(text)
        return "\n".join(parts) if parts else None
    except Exception:
        return None


def try_ocr_on_pdf(file_bytes_or_io) -> Optional[str]:
    """Run OCR on PDF bytes if standard extraction failed."""
    if hasattr(file_bytes_or_io, "read"):
        file_bytes = file_bytes_or_io.read()
        file_bytes_or_io.seek(0)
    elif isinstance(file_bytes_or_io, bytes):
        file_bytes = file_bytes_or_io
    else:
        with open(file_bytes_or_io, "rb") as f:
            file_bytes = f.read()
    return extract_text_with_ocr(file_bytes)
