import io
from typing import Optional
from pdfminer.high_level import extract_text as pdf_extract_text
from docx import Document

SUPPORTED_EXT = {".pdf", ".docx", ".txt"}


def _ext_of(filename: str) -> str:
    low = filename.lower()
    for ext in SUPPORTED_EXT:
        if low.endswith(ext):
            return ext
    return ""


def extract_text_from_file(filename: str, content: bytes) -> str:
    ext = _ext_of(filename)
    if ext == ".pdf":
        # pdfminer.six supports file-like objects
        with io.BytesIO(content) as f:
            return pdf_extract_text(f) or ""
    elif ext == ".docx":
        with io.BytesIO(content) as f:
            doc = Document(f)
            return "\n".join(p.text for p in doc.paragraphs)
    elif ext == ".txt":
        try:
            return content.decode("utf-8", errors="ignore")
        except Exception:
            return content.decode(errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {filename}")
