// Simple real-time streaming test
const https = require('https');
const http = require('http');

console.log('Starting real-time streaming test...');

const postData = JSON.stringify({
  prompt: 'What are the latest developments in artificial intelligence?'
});

const options = {
  hostname: 'localhost',
  port: 8080,
  path: '/api/v1/ai/stream-search',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(postData)
  }
};

const req = http.request(options, (res) => {
  console.log(`Status: ${res.statusCode}`);
  console.log('Headers:', res.headers);
  
  res.on('data', (chunk) => {
    console.log(`Received chunk (${chunk.length} bytes):`);
    console.log(chunk.toString());
  });
  
  res.on('end', () => {
    console.log('Stream ended');
  });
});

req.on('error', (e) => {
  console.error(`Problem with request: ${e.message}`);
});

req.write(postData);
req.end();