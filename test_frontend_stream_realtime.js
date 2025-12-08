// Test frontend streaming in real-time
async function testFrontendStreamRealtime() {
  try {
    console.log('Starting real-time streaming test...');
    
    const response = await fetch('http://localhost:8080/api/v1/ai/stream-search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt: 'What are the latest developments in artificial intelligence?' }),
    });

    if (!response.body) {
      throw new Error('ReadableStream not supported');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    console.log('Receiving real-time updates:');
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        console.log('Stream complete');
        break;
      }
      
      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split('\n\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.substring(6));
            console.log(`Received: ${data.type} - ${JSON.stringify(data)}`);
          } catch (e) {
            console.error('Error parsing JSON:', e);
          }
        }
      }
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

testFrontendStreamRealtime();