import requests
import json

def test_stream():
    url = "http://127.0.0.1:8000/stream"
    payload = {
        "prompt": "Explain what artificial intelligence is in simple terms"
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    print("Testing streaming endpoint...")
    print("-" * 50)
    
    with requests.post(url, json=payload, headers=headers, stream=True) as r:
        for line in r.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data: '):
                    try:
                        data = json.loads(decoded_line[6:])  # Remove 'data: ' prefix
                        print(f"Event Type: {data['type']}")
                        print(f"Data: {data['data']}")
                        print("-" * 30)
                    except json.JSONDecodeError:
                        print(f"Raw line: {decoded_line}")

if __name__ == "__main__":
    test_stream()