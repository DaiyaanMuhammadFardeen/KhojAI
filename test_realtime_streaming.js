// Test real-time streaming with timestamps to show immediate delivery
async function testRealTimeStreaming() {
  try {
    console.log('🧪 Starting real-time streaming test...');
    console.log('🕒 Timestamp format: [HH:MM:SS.ms]');
    
    const startTime = Date.now();
    
    const response = await fetch('http://localhost:8080/api/v1/ai/stream-search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt: 'What are the latest developments in quantum computing?' }),
    });

    if (!response.body) {
      throw new Error('ReadableStream not supported');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    console.log('\n📡 Receiving real-time streaming data:');
    console.log('=====================================');
    
    let eventCount = 0;
    
    while (true) {
      const { done, value } = await reader.read();
      const currentTime = Date.now();
      const elapsed = currentTime - startTime;
      
      if (done) {
        console.log(`\n✅ Stream complete at ${formatTime(currentTime)} (Total time: ${elapsed}ms)`);
        break;
      }
      
      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split('\n\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.substring(6));
            eventCount++;
            
            // Show different information based on event type
            switch (data.type) {
              case 'analysis':
                if (data.status === 'started') {
                  console.log(`[${formatTime(currentTime)}] 🔍 Prompt analysis started`);
                } else if (data.status === 'completed') {
                  console.log(`[${formatTime(currentTime)}] ✅ Analysis completed (${elapsed}ms)`);
                  console.log(`     Search queries: ${data.search_queries ? data.search_queries.length : 0} generated`);
                }
                break;
                
              case 'search':
                if (data.status === 'started') {
                  console.log(`[${formatTime(currentTime)}] 🔎 Search started: "${data.query}"`);
                } else if (data.status === 'completed') {
                  console.log(`[${formatTime(currentTime)}] ✅ Search completed: ${data.results_count} results (${elapsed}ms)`);
                }
                break;
                
              case 'urls_found':
                console.log(`[${formatTime(currentTime)}] 🌐 URLs found: ${data.count} URLs`);
                break;
                
              case 'scraping':
                if (data.status === 'started') {
                  console.log(`[${formatTime(currentTime)}] 📥 Scraping started: ${shortenUrl(data.url)}`);
                } else if (data.status === 'completed') {
                  console.log(`[${formatTime(currentTime)}] ✅ Scraping completed: ${shortenUrl(data.url)}`);
                }
                break;
                
              case 'scraping_error':
                console.log(`[${formatTime(currentTime)}] ❌ Scraping error: ${shortenUrl(data.url)} - ${data.error}`);
                break;
                
              case 'extracting':
                if (data.status === 'started') {
                  console.log(`[${formatTime(currentTime)}] 🔍 Extracting started: ${shortenUrl(data.url)}`);
                } else if (data.status === 'completed') {
                  console.log(`[${formatTime(currentTime)}] ✅ Extracting completed: ${data.sentences_count} sentences`);
                }
                break;
                
              case 'search_result':
                console.log(`[${formatTime(currentTime)}] 📄 Result: ${data.title} (${data.sentences_count} sentences)`);
                break;
                
              case 'deduplication':
                console.log(`[${formatTime(currentTime)}] 🧹 Deduplication: ${data.original_count} → ${data.final_count} results`);
                break;
                
              case 'response_generation':
                if (data.status === 'started') {
                  console.log(`[${formatTime(currentTime)}] 🧠 Response generation started`);
                } else if (data.status === 'completed') {
                  console.log(`[${formatTime(currentTime)}] ✅ Response generation completed`);
                }
                break;
                
              case 'final_response':
                console.log(`[${formatTime(currentTime)}] 🤖 Final response generated (${data.message.length} chars)`);
                break;
                
              case 'done':
                console.log(`[${formatTime(currentTime)}] 🏁 Streaming finished`);
                break;
            }
          } catch (e) {
            console.error(`[${formatTime(currentTime)}] Error parsing JSON:`, e.message);
          }
        }
      }
    }
    
    console.log(`\n📊 Summary:`);
    console.log(`   • Total events received: ${eventCount}`);
    console.log(`   • Total time elapsed: ${Date.now() - startTime}ms`);
    
  } catch (error) {
    console.error('💥 Error:', error);
  }
}

// Helper function to format timestamp
function formatTime(timestamp) {
  const date = new Date(timestamp);
  return date.toISOString().substr(11, 12); // HH:MM:SS.ms
}

// Helper function to shorten URLs for display
function shortenUrl(url) {
  if (url.length <= 50) return url;
  return url.substr(0, 47) + '...';
}

testRealTimeStreaming();