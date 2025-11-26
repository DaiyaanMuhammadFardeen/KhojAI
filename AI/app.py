from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from prompt_analyzer import analyze_prompt
from ai_orchestrator import generate_response_with_web_search
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Prompt Analyzer", version="1.0.0")

# Warm up the model when the application starts
@app.on_event("startup")
async def warmup_model():
    logger.info("Warming up the model...")
    try:
        response = ollama.generate(
            model="gemma3:1b",
            prompt="hi",
            stream=False
        )
        logger.info("Model warmed up successfully")
    except Exception as e:
        logger.error(f"Error warming up model: {str(e)}")

class PromptRequest(BaseModel):
    prompt: str

class PromptResponse(BaseModel):
    message: str

@app.post("/analyze")
async def analyze(request: PromptRequest):
    logger.info(f"Analyzing prompt: {request.prompt}")
    try:
        result = analyze_prompt(request.prompt, debug=False)
        logger.info(f"Analysis result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-response", response_model=PromptResponse)
async def generate_response(request: PromptRequest):
    """
    Generate a response using web search and LLM augmentation.
    """
    logger.info(f"Generating response for prompt: {request.prompt}")
    try:
        response = generate_response_with_web_search(request.prompt)
        logger.info(f"Generated response: {response}")
        return PromptResponse(message=response)
    except Exception as e:
        logger.error(f"Error in generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")