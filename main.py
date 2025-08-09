import os
import traceback
from dotenv import load_dotenv
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from resume_parser import extract_text
from ai_client import recommend_jobs_from_text   # <-- should now use Groq!

# Load environment variables from .env file
load_dotenv()
print("Loaded API Key:", os.getenv("GROQ_API_KEY"))  # <-- Changed to GROQ_API_KEY (matches Groq doc)

app = FastAPI(title='SmartRecruitAI')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(__file__)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, 'templates'))
app.mount('/static', StaticFiles(directory=os.path.join(BASE_DIR, 'static')), name='static')

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})

@app.post('/analyze', response_class=HTMLResponse)
async def analyze(request: Request, file: UploadFile = File(...)):
    try:
        contents = await file.read()
        text = extract_text(file.filename, contents)
        if not text.strip():
            return templates.TemplateResponse(
                'index.html',
                {"request": request, "error": 'Could not extract text from the file. Try a PDF or DOCX.'}
            )

        ai_result = await recommend_jobs_from_text(text)   # This should use GROQ_API_KEY inside ai_client.py!
        return templates.TemplateResponse(
            'result.html',
            {"request": request, "result": ai_result, "filename": file.filename}
        )
    except Exception as e:
        traceback.print_exc()
        return templates.TemplateResponse(
            'index.html',
            {"request": request, "error": 'Internal server error: ' + str(e)}
        )

