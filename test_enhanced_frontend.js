// Enhanced frontend test with detailed real-time updates
async function testEnhancedFrontend() {
  try {
    console.log('Starting enhanced real-time search test...\n');
    
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

    console.log('Receiving real-time updates:\n');
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        console.log('\n✅ Stream complete');
        break;
      }
      
      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split('\n\n');
      
      lines.forEach(line => {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.substring(6));
            
            switch (data.type) {
              case 'analysis':
                if (data.status === 'started') {
                  console.log(`🔍 Analyzing: ${data.message}`);
                } else if (data.status === 'completed') {
                  console.log(`✅ Analysis complete`);
                  if (data.search_queries) {
                    console.log(`   Search queries: ${data.search_queries.join(', ')}`);
                  }
                }
                break;
                
              case 'search':
                if (data.status === 'started') {
                  console.log(`🔎 Searching web for: "${data.query}"`);
                } else if (data.status === 'completed') {
                  console.log(`   ✅ Found ${data.results_count} results`);
                }
                break;
                
              case 'urls_found':
                console.log(`   🌐 Found ${data.count} URLs for query: "${data.query}"`);
                break;
                
              case 'scraping':
                if (data.status === 'started') {
                  console.log(`   📥 Scraping: ${data.url}`);
                } else if (data.status === 'completed') {
                  console.log(`   ✅ Scraped: ${data.title}`);
                }
                break;
                
              case 'scraping_error':
                console.log(`   ❌ Error scraping ${data.url}: ${data.error}`);
                break;
                
              case 'extracting':
                if (data.status === 'started') {
                  console.log(`   🔍 Extracting information from: ${data.url}`);
                } else if (data.status === 'completed') {
                  console.log(`   ✅ Extracted ${data.sentences_count} relevant sentences`);
                }
                break;
                
              case 'search_result':
                console.log(`   📄 Result: ${data.title} (${data.sentences_count} sentences)`);
                break;
                
              case 'deduplication':
                console.log(`   🧹 Removed ${data.original_count - data.final_count} duplicate results`);
                break;
                
              case 'response_generation':
                if (data.status === 'started') {
                  console.log(`🧠 Generating final response...`);
                } else if (data.status === 'completed') {
                  console.log(`   ✅ Response generated`);
                }
                break;
                
              case 'final_response':
                console.log(`\n🤖 Final AI Response:`);
                console.log(`${data.message}\n`);
                break;
                
              case 'done':
                console.log(`✅ Done`);
                break;
                
              case 'error':
                console.log(`❌ Error: ${data.message}`);
                break;
            }
          } catch (e) {
            console.error('Error parsing JSON:', e);
          }
        }
      });
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

testEnhancedFrontend();