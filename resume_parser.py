import io
from PyPDF2 import PdfReader
from docx import Document

def extract_text_from_pdf(file_bytes: bytes) -> str:
    # Extracts text from all pages of a PDF
    reader = PdfReader(io.BytesIO(file_bytes))
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(texts)

def extract_text_from_docx(file_bytes: bytes) -> str:
    # Extracts all text from a DOCX file
    with io.BytesIO(file_bytes) as f:
        doc = Document(f)
        return "\n".join(p.text for p in doc.paragraphs)

def extract_text(filename: str, file_bytes: bytes) -> str:
    """
    Attempt to extract text from a file.
    - Uses PDF for .pdf;
    - DOCX for .docx/.doc;
    - Tries UTF-8 decode for others (.txt).
    """
    lower = filename.lower()
    if lower.endswith('.pdf'):
        return extract_text_from_pdf(file_bytes)
    if lower.endswith('.docx') or lower.endswith('.doc'):
        return extract_text_from_docx(file_bytes)
    try:
        return file_bytes.decode('utf-8', errors='ignore')
    except Exception:
        return ''
