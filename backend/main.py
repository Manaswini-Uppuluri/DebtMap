from flask import Flask, request, jsonify
from flask_cors import CORS
from openclaw_adapter import openclaw_run
from scanner import scan_code

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "API running"})

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    code = data.get("code", "")

    if not code:
        return jsonify({"error": "No code provided"}), 400

    try:
        # Step 1: scan code
        scan_results = scan_code(code)

        if not scan_results:
            return jsonify({
                "status": "no_issues",
                "message": "No deprecated APIs found"
            })

        # Step 2: take first issue
        detection = scan_results[0]

        input_data = {
            "old_usage": detection.get("old_usage", "unknown"),
            "new_api": detection.get("new_api", "unknown"),
            "reason": detection.get("reason", "Not specified"),
            "code_snippet": code
        }

        # Step 3: AI agent
        result = openclaw_run(input_data)

        return jsonify({
            "status": "success",
            "scan_result": detection,
            "ai_result": result
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)