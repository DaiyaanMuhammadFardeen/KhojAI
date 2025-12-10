from typing import Dict, Any, AsyncGenerator
from datetime import datetime
import json

class StreamEvent:
    """
    Standardized streaming event format for all stages of the AI processing pipeline.
    """
    def __init__(self, event_type: str, data: Dict[str, Any]):
        self.type = event_type
        self.data = data
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "type": self.type,
            "data": self.data,
            "timestamp": self.timestamp
        }
    
    def to_json(self):
        return json.dumps(self.to_dict())

# Event types constants
EVENT_TYPES = {
    "INTENT_DETECTED": "intent_detected",
    "SEARCH_STARTED": "search_started",
    "SEARCH_PROGRESS": "search_progress",
    "SEARCH_RESULT": "search_result",
    "SEARCH_COMPLETED": "search_completed",
    "RESPONSE_STARTED": "response_started",
    "RESPONSE_TOKEN": "response_token",
    "RESPONSE_COMPLETED": "response_completed",
    "PROCESSING_ERROR": "processing_error",
    "STREAM_COMPLETE": "stream_complete"
}