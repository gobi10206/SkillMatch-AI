"""
Resume text extraction. Supports PDF (pdfplumber) and DOCX
(python-docx). Raw uploaded files are processed in memory and NOT
persisted to disk/DB by default — see Phase 37 rule: "Do not
permanently store raw uploaded documents unless necessary and
authorized."
"""
import io

import pdfplumber
from docx import Document

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5MB
ALLOWED_CONTENT_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}


class UnsupportedFileError(Exception):
    pass


def extract_text(file_bytes: bytes, content_type: str) -> str:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise UnsupportedFileError(f"Unsupported file type: {content_type}")
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise UnsupportedFileError("File exceeds maximum upload size (5MB)")

    kind = ALLOWED_CONTENT_TYPES[content_type]
    if kind == "pdf":
        return _extract_pdf(file_bytes)
    return _extract_docx(file_bytes)


def _extract_pdf(file_bytes: bytes) -> str:
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def _extract_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
