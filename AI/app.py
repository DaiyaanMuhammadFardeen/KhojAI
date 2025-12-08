from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import json
import asyncio
import traceback
from prompt_analyzer import analyze_prompt
from ai_orchestrator import generate_response_with_web_search_stream, generate_response_with_web_search

app = FastAPI(title="AI Prompt Analyzer", version="1.0.0")

class PromptRequest(BaseModel):
    prompt: str

class PromptResponse(BaseModel):
    message: str

# Add a new streaming endpoint for real-time search updates
@app.post("/stream-search")
async def stream_search_updates(request: PromptRequest):
    """
    Stream search updates in real-time as they happen.
    """
    print(f"Received streaming request with prompt: {request.prompt}")
    try:
        return StreamingResponse(generate_response_with_web_search_stream(request.prompt),
                                 media_type="text/event-stream",
                                 headers={
                                 "Cache-Control": "no-cache",
                                 "Connection": "keep-alive",
                                 "Access-Control-Allow-Origin": "*",
                                 "X-Accel-Buffering": "no"  # Disable buffering for nginx
                                 })
    except Exception as e:
        print(f"Error in stream_search_updates: {str(e)}")
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
        # Handle case where prompt might be empty or malformed
        if not request.prompt or not request.prompt.strip():
            return PromptResponse(message="I didn't receive any input. Could you please provide a question or message?")

        response = generate_response_with_web_search(request.prompt)
        # Handle case where response might be None or empty
        if not response or not response.strip():
            return PromptResponse(message="I couldn't generate a response to that. Could you try rephrasing?")

        return PromptResponse(message=response)
    except IndexError as e:
        # Specifically handle index errors
        print(f"Index error in AI processing: {e}")
        return PromptResponse(message="I encountered an issue processing your request. Could you try rephrasing it?")
    except Exception as e:
        print(f"Error in generate_response: {e}")
        print(traceback.format_exc())
        # Return a user-friendly error message instead of raising HTTPException
        return PromptResponse(message="I encountered an unexpected error while processing your request. Please try again.")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
