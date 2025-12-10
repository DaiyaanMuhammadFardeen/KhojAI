from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import json
import asyncio
import traceback
from prompt_analyzer import analyze_prompt
from ai_orchestrator import generate_response_with_web_search, generate_unified_stream

app = FastAPI(title="AI Prompt Analyzer", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

class PromptRequest(BaseModel):
    prompt: str

# Alternative request model for more flexible handling
class FlexiblePromptRequest(BaseModel):
    prompt: str = None
    query: str = None
    message: str = None
    text: str = None

@app.post("/stream")
async def unified_stream(request: Request):
    """
    Unified streaming endpoint that combines intent analysis, search, and response generation.
    Handles various request formats for compatibility with different clients.
    """
    try:
        # Try to parse the request body
        body = await request.json()
        
        # Extract prompt from various possible field names
        prompt = (body.get('prompt') or 
                 body.get('query') or 
                 body.get('message') or 
                 body.get('text') or 
                 "")
        
        # If we still don't have a prompt, raise an error
        if not prompt:
            raise HTTPException(status_code=400, detail="No prompt provided in request")
            
        print(f"Received unified streaming request with prompt: {prompt}")
        
        return StreamingResponse(generate_unified_stream(prompt),
                                 media_type="text/event-stream",
                                 headers={
                                 "Cache-Control": "no-cache",
                                 "Connection": "keep-alive",
                                 "Access-Control-Allow-Origin": "*",
                                 "X-Accel-Buffering": "no"  # Disable buffering for nginx
                                 })
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except Exception as e:
        print(f"Error in unified_stream: {str(e)}")
        print(traceback.format_exc())
        # Even in case of error, send a proper response
        error_message = json.dumps({"type": "error", "message": "An error occurred while processing your request"})
        return StreamingResponse(iter([f"data: {error_message}\n\n"]),
                                 media_type="text/event-stream",
                                 headers={
                                 "Cache-Control": "no-cache",
                                 "Connection": "keep-alive",
                                 "Access-Control-Allow-Origin": "*"
                                 })

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
    uvicorn.run(app, host="0.0.0.0", port=8000)