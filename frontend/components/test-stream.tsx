'use client';

import React, { useState } from 'react';
import { AIApi } from '@/app/api/chat/route';

export default function TestStream() {
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  
  const test = async () => {
    setEvents([]);
    setLoading(true);
    
    try {
      await AIApi.streamSearch(
        { prompt: "test" },
        (data) => {
          console.log("Received:", data);
          setEvents(prev => [...prev, data]);
        },
        () => {
          console.log("Complete");
          setLoading(false);
        },
        (err) => {
          console.error("Error:", err);
          setLoading(false);
        }
      );
    } catch (error) {
      console.error("Test failed:", error);
      setLoading(false);
    }
  };
  
  return (
    <div className="p-4">
      <button 
        onClick={test} 
        disabled={loading}
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
      >
        {loading ? 'Testing...' : 'Test Stream'}
      </button>
      
      <div className="mt-4">
        <h3 className="text-lg font-semibold">Events:</h3>
        <pre className="bg-gray-100 p-2 mt-2 overflow-auto max-h-96">
          {JSON.stringify(events, null, 2)}
        </pre>
      </div>
    </div>
  );
}