// Simulate frontend streaming
async function testFrontendStream() {
  try {
    const response = await fetch('http://localhost:8080/api/v1/ai/stream-search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt: 'What is the weather today?' }),
    });

    if (!response.body) {
      throw new Error('ReadableStream not supported');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    console.log('Starting to read stream...');
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        console.log('Stream complete');
        break;
      }
      
      const chunk = decoder.decode(value, { stream: true });
      console.log('Received chunk:', chunk);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

testFrontendStream();