'use client';

import React, { useState, useRef } from 'react';

export default function StreamTestPage() {
  const [input, setInput] = useState('What is the latest news today?');
  const [isLoading, setIsLoading] = useState(false);
  const [events, setEvents] = useState<any[]>([]);
  const [currentResponse, setCurrentResponse] = useState('');
  const eventEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom function
  const scrollToBottom = () => {
    eventEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    setIsLoading(true);
    setEvents([]);
    setCurrentResponse('');

    try {
      // Connect to Java Spring Boot backend instead of Python directly
    const response = await fetch('http://127.0.0.1:8000/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: input }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          // Flush any remaining buffer
          if (buffer.trim()) {
            // Process any remaining data
            const part = buffer.trim();
            if (part.startsWith('data: ')) {
              const jsonData = part.slice(6);
              try {
                const json = JSON.parse(jsonData);
                setEvents(prev => [...prev, {
                  ...json,
                  timestamp: new Date().toLocaleTimeString()
                }]);
                
                if (json.type === 'response_token') {
                  setCurrentResponse(prev => prev + json.token);
                } else if (json.type === 'search_progress') {
                  setCurrentResponse(prev => prev + `\n[Searching: ${json.data?.query || 'Unknown'}]`);
                } else if (json.type === 'search_result') {
                  setCurrentResponse(prev => prev + `\n• ${json.data?.title || 'Untitled'} (${json.data?.url || 'No URL'})`);
                }
              } catch (e) {
                console.warn('Failed to parse SSE event:', jsonData);
              }
            }
          }
          setEvents(prev => [...prev, { type: 'stream_complete', data: '[END OF STREAM]' }]);
          break;
        }

        buffer += decoder.decode(value, { stream: true });

        // Split on complete SSE events (separated by \n\n)
        let parts = buffer.split('\n\n');
        
        // Keep the last incomplete part
        buffer = parts.pop() || '';

        // Process all complete events
        for (let part of parts) {
          part = part.trim();
          if (!part) continue;

          // Remove 'data: ' prefix if present
          if (part.startsWith('data: ')) {
            part = part.slice(6);
          }

          try {
            const json = JSON.parse(part);

            setEvents(prev => [...prev, {
              ...json,
              timestamp: new Date().toLocaleTimeString()
            }]);

            // Handle response tokens
            if (json.type === 'response_token') {
              setCurrentResponse(prev => prev + json.token);
            } else if (json.type === 'search_progress') {
              setCurrentResponse(prev => prev + `\n[Searching: ${json.data?.query || 'Unknown'}]`);
            } else if (json.type === 'search_result') {
              setCurrentResponse(prev => prev + `\n• ${json.data?.title || 'Untitled'} (${json.data?.url || 'No URL'})`);
            }
            
            // Scroll to new event
            setTimeout(scrollToBottom, 0);
          } catch (e) {
            console.warn('Failed to parse SSE event:', part);
            setCurrentResponse(prev => prev + part);
          }
        }
      }
    } catch (error) {
      console.error('Stream error:', error);
      setEvents(prev => [...prev, {
        type: 'error',
        data: error instanceof Error ? error.message : 'Unknown error occurred',
        timestamp: new Date().toLocaleTimeString()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Clear all events
  const handleClear = () => {
    setEvents([]);
    setCurrentResponse('');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Java AI Stream Test</h1>
        <p className="text-gray-600 mb-6">Connection to Java /stream-ai-response endpoint</p>

        <form onSubmit={handleSubmit} className="mb-8">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Enter prompt to test..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? 'Streaming...' : 'Send'}
            </button>
            <button
              type="button"
              onClick={handleClear}
              className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
            >
              Clear
            </button>
          </div>
        </form>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Live Response Display */}
          <div className="bg-white rounded-lg shadow p-4">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Live Response</h2>
            <div className="border border-gray-200 rounded p-4 min-h-[300px] max-h-[500px] overflow-y-auto bg-gray-50 font-mono whitespace-pre-wrap">
              {currentResponse || (
                <p className="text-gray-500 italic">
                  {isLoading ? 'Waiting for response...' : 'Response will appear here'}
                </p>
              )}
            </div>
          </div>

          {/* Event Log */}
          <div className="bg-white rounded-lg shadow p-4">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Event Log</h2>
            <div className="border border-gray-200 rounded p-4 min-h-[300px] max-h-[500px] overflow-y-auto">
              {events.length > 0 ? (
                <ul className="space-y-3">
                  {events.map((event, index) => (
                    <li key={index} className="py-2 border-b border-gray-100 last:border-b-0">
                      <div className="flex justify-between items-start">
                        <span className={`font-medium text-sm ${
                          event.type === 'error' ? 'text-red-500' :
                          event.type === 'stream_complete' ? 'text-green-500' :
                          event.type === 'response_token' ? 'text-blue-500' :
                          event.type === 'search_progress' ? 'text-purple-500' :
                          event.type === 'search_result' ? 'text-indigo-500' :
                          event.type === 'raw' ? 'text-yellow-500' :
                          event.type === 'unknown' ? 'text-orange-500' : 'text-gray-500'
                        }`}>
                          {event.type || 'unknown'}
                        </span>
                        <span className="text-xs text-gray-400">
                          {event.timestamp || new Date().toLocaleTimeString()}
                        </span>
                      </div>
                      <div className="text-gray-800 mt-1 whitespace-pre-wrap break-words">
                        {typeof event.data === 'string' ? event.data : JSON.stringify(event.data, null, 2)}
                      </div>
                    </li>
                  ))}
                  <div ref={eventEndRef} />
                </ul>
              ) : (
                <p className="text-gray-500 italic">
                  {isLoading ? 'Waiting for events...' : 'Events will appear here'}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Status Indicator */}
        <div className="mt-6 flex items-center justify-center">
          <div className={`w-3 h-3 rounded-full mr-2 ${isLoading ? 'bg-green-500 animate-pulse' : 'bg-gray-300'}`}></div>
          <span className="text-gray-600">
            {isLoading ? 'Receiving stream data...' : 'Idle'}
          </span>
        </div>
      </div>
    </div>
  );
}