// Demo real-time streaming from backend to show immediate data reception
async function demoRealTimeStreaming() {
  console.log('🚀 Real-time Streaming Demo');
  console.log('========================');
  console.log('Connecting to backend service at http://localhost:8080/api/v1/ai/stream-search\n');
  
  try {
    const response = await fetch('http://localhost:8080/api/v1/ai/stream-search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        prompt: 'What are the latest developments in artificial intelligence?' 
      }),
    });

    if (!response.body) {
      throw new Error('ReadableStream not supported');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    console.log('📡 Receiving real-time streaming data...\n');

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        console.log('\n✅ Stream complete!');
        break;
      }
      
      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split('\n\n');
      
      lines.forEach(line => {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.substring(6));
            
            // Display real-time updates with emojis for better visualization
            switch (data.type) {
              case 'analysis':
                if (data.status === 'started') {
                  console.log(`🔍 ${data.message}`);
                } else if (data.status === 'completed') {
                  console.log(`✅ Analysis completed`);
                }
                break;
                
              case 'search':
                if (data.status === 'started') {
                  console.log(`🔎 Searching: "${data.query}"`);
                } else if (data.status === 'completed') {
                  console.log(`   ✅ Found ${data.results_count} results`);
                }
                break;
                
              case 'urls_found':
                console.log(`   🌐 ${data.count} URLs discovered`);
                break;
                
              case 'scraping':
                if (data.status === 'started') {
                  console.log(`📥 Scraping: ${data.url.substring(0, 60)}${data.url.length > 60 ? '...' : ''}`);
                } else if (data.status === 'completed') {
                  console.log(`   ✅ Scraped: ${data.title}`);
                }
                break;
                
              case 'scraping_error':
                console.log(`   ❌ Error: ${data.url} - ${data.error}`);
                break;
                
              case 'extracting':
                if (data.status === 'started') {
                  console.log(`🔍 Extracting from: ${data.url.substring(0, 60)}${data.url.length > 60 ? '...' : ''}`);
                } else if (data.status === 'completed') {
                  console.log(`   ✅ Extracted ${data.sentences_count} sentences`);
                }
                break;
                
              case 'search_result':
                console.log(`📄 ${data.title} (${data.sentences_count} sentences)`);
                break;
                
              case 'deduplication':
                console.log(`🧹 Deduplication: ${data.original_count} → ${data.final_count}`);
                break;
                
              case 'response_generation':
                if (data.status === 'started') {
                  console.log(`🧠 Generating response...`);
                } else if (data.status === 'completed') {
                  console.log(`   ✅ Response generated`);
                }
                break;
                
              case 'final_response':
                console.log(`\n🤖 Final AI Response:`);
                console.log(`"${data.message.substring(0, 200)}${data.message.length > 200 ? '...' : ''}"`);
                if (data.message.length > 200) {
                  console.log(`   (Response truncated. Full response: ${data.message.length} characters)`);
                }
                break;
                
              case 'done':
                console.log(`🏁 Done`);
                break;
            }
          } catch (e) {
            console.error('Error parsing JSON:', e.message);
          }
        }
      });
    }
  } catch (error) {
    console.error('💥 Error:', error.message);
  }
}

// Run the demo
demoRealTimeStreaming();