import pytest
from fastapi.testclient import TestClient
import io
from main import app

client = TestClient(app)

def test_root():
    r = client.get('/')
    assert r.status_code == 200
    assert 'SmartRecruitAI' in r.text

def test_analyze_text_file():
    # simple text resume
    data = {
        'file': ('resume.txt', io.BytesIO(b"Experienced in Python, Flask, AWS and React"), 'text/plain')
    }
    r = client.post('/analyze', files=data, allow_redirects=True)
    assert r.status_code == 200
    # Should show recommended titles in the HTML
    assert 'Recommended Titles' in r.text
