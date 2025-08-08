import io
from PyPDF2 import PdfReader
from docx import Document

def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(texts)

def extract_text_from_docx(file_bytes: bytes) -> str:
    with io.BytesIO(file_bytes) as f:
        doc = Document(f)
        return "\n".join(p.text for p in doc.paragraphs)

def extract_text(filename: str, file_bytes: bytes) -> str:
    lower = filename.lower()
    if lower.endswith('.pdf'):
        return extract_text_from_pdf(file_bytes)
    if lower.endswith('.docx') or lower.endswith('.doc'):
        return extract_text_from_docx(file_bytes)
    try:
        return file_bytes.decode('utf-8', errors='ignore')
    except Exception:
        return ''
