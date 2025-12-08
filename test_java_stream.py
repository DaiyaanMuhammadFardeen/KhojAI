import requests
import json

response = requests.post('http://localhost:8080/api/v1/ai/stream-search', 
                        json={'prompt': 'What is the weather today?'}, 
                        stream=True)

print('Status code:', response.status_code)
for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))