from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from prompt_analyzer import analyze_prompt
from ai_orchestrator import generate_response_with_web_search

app = FastAPI(title="AI Prompt Analyzer", version="1.0.0")

class PromptRequest(BaseModel):
    prompt: str

class PromptResponse(BaseModel):
    message: str

@app.post("/analyze")
async def analyze(request: PromptRequest):
    try:
        result = analyze_prompt(request.prompt, debug=False)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-response", response_model=PromptResponse)
async def generate_response(request: PromptRequest):
    """
    Generate a response using web search and LLM augmentation.
    """
    try:
        response = generate_response_with_web_search(request.prompt)
        return PromptResponse(message=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")