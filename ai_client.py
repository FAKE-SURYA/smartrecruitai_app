import os, json, re
from typing import Dict, Any, List
import httpx
import logging

from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = os.getenv('GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')
print("GROQ_API_KEY loaded in ai_client.py:", GROQ_API_KEY)


# ----- NO sentence-transformers logic below this line unless needed ------

async def call_groq_chat(prompt: str) -> Dict[str, Any]:
    headers = {
        'Authorization': f'Bearer {GROQ_API_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        'model': 'llama3-8b-8192',   # Groq’s cheapest/fastest model, you can change if needed
        'messages': [
            { 'role': 'system', 'content': 'You are a helpful assistant that extracts job title recommendations from resumes and returns a JSON object.' },
            { 'role': 'user', 'content': prompt }
        ],
        'max_tokens': 500,
        'temperature': 0.1,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(GROQ_API_URL, headers=headers, json=payload)
        r.raise_for_status()
        return r.json()

def heuristic_recommend(text: str) -> Dict:
    tokens = re.findall(r"\w+", text.lower())
    keywords = set(tokens)
    titles = []
    if any(k in keywords for k in ('python', 'django', 'flask')):
        titles.append('Backend Engineer / Python Developer')
    if any(k in keywords for k in ('react', 'javascript', 'vue', 'frontend')):
        titles.append('Frontend Engineer / React Developer')
    if any(k in keywords for k in ('aws', 'azure', 'gcp', 'cloud', 'devops')):
        titles.append('Cloud Engineer / DevOps Engineer')
    if any(k in keywords for k in ('machine', 'learning', 'nlp', 'data', 'tensorflow', 'pytorch')):
        titles.append('Machine Learning Engineer / Data Scientist')
    if not titles:
        titles = ['Software Engineer (General)']

    scores = {t: round(0.7 + 0.2 * (i / max(1, len(titles)-1)), 2) for i, t in enumerate(titles)}
    highlights = ['Detected skills sample: ' + ', '.join(sorted([w for w in keywords if len(w) > 3])[:20])]
    return {
        'recommended_titles': titles,
        'confidence_scores': scores,
        'highlights': highlights,
        'explanation': 'Heuristic fallback used. Set GROQ_API_KEY to enable richer LLM output.'
    }

def _try_parse_json(text: str) -> Any:
    # Try to find a JSON object inside text
    try:
        return json.loads(text)
    except Exception:
        # Attempt to extract {...} using regex
        m = re.search(r"\{.*\}", text, flags=re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
    return None

async def recommend_jobs_from_text(text: str) -> Dict:
    # If GROQ key available, prefer LLM
    if GROQ_API_KEY:
        prompt = (
            "Given the following resume text, return a JSON object with keys: 'recommended_titles' (list of strings),"
            " 'confidence_scores' (map title->float between 0 and 1), 'highlights' (list of strings), and 'explanation' (string).\n\n"
            "Resume:\n" + text[:6000]
        )
        try:
            resp = await call_groq_chat(prompt)
            assistant_msg = resp['choices'][0]['message']['content']
            parsed = _try_parse_json(assistant_msg)
            if parsed and isinstance(parsed, dict):
                # Ensure required keys
                for k in ('recommended_titles','confidence_scores','highlights','explanation'):
                    if k not in parsed:
                        return heuristic_recommend(text)
                return parsed
            else:
                return heuristic_recommend(text)
        except Exception as e:
            logging.exception('Groq call failed, falling back to heuristic')
            return heuristic_recommend(text)
    else:
        # fallback, works but less powerful
        return heuristic_recommend(text)
