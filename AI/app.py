from flask import Flask, request, jsonify
from prompt_analyzer import analyze_prompt

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    payload = request.get_json(force=True)
    result = analyze_prompt(payload.get("prompt", ""), debug=False)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)

