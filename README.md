# SmartRecruitAI (Pure-Python)
Single-repo FastAPI app that analyzes resumes and recommends job titles.

Features:
- FastAPI + Jinja2 templates (no separate frontend)
- Resume parsing (PDF, DOCX, TXT)
- AI client: OpenAI ChatCompletion integration (if OPENAI_API_KEY set) + heuristic fallback
- Optional sentence-transformers embedding-based ranking (if installed)
- Unit tests and GitHub Actions CI workflow

Run (dev):
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

To enable LLM responses, set environment variable `OPENAI_API_KEY` with your OpenAI API key.
