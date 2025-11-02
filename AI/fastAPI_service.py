# fastapi_service.py
from fastapi import FastAPI
from prompt_analyzer import analyze_prompt

app = FastAPI()

@app.post("/analyze")
def api_analyze(payload: dict):
    return analyze_prompt(payload.get("prompt", ""), debug=False)
