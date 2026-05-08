import os
import shutil
import subprocess
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
from openclaw_adapter import openclaw_run
from scanner import scan_code

app = Flask(__name__)
CORS(app)

def scan_directory(directory_path):
    all_findings = []
    print(f"DEBUG: Starting deep scan of {directory_path}")
    for root, dirs, files in os.walk(directory_path):
        if '.git' in dirs: dirs.remove('.git')
        if '__pycache__' in dirs: dirs.remove('__pycache__')
        
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.java', '.html', '.css')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        findings = scan_code(content)
                        if findings:
                            for finding in findings:
                                finding['file'] = os.path.relpath(file_path, directory_path)
                                # Crucial: Pass full content for the "View in Editor" feature
                                finding['full_content'] = content
                                finding['estimated_cost'] = finding.get('estimated_cost', 50)
                                finding['effort'] = finding.get('effort', 'Medium')
                                all_findings.append(finding)
                except Exception as e:
                    print(f"DEBUG: Failed to read {file}: {e}")
    return all_findings

@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    code = data.get("code", "")
    repo_url = data.get("repo_url", "")
    temp_dir = tempfile.mkdtemp()
    
    try:
        scan_results = []
        if repo_url:
            print(f"DEBUG: Cloning {repo_url}...")
            subprocess.run(f'git clone --depth 1 "{repo_url}" "{temp_dir}"', shell=True, check=True, timeout=60)
            scan_results = scan_directory(temp_dir)
        else:
            scan_results = scan_code(code)
            for r in scan_results: 
                r['file'] = "manual_input.py"
                r['full_content'] = code
                r['estimated_cost'] = r.get('estimated_cost', 50)
                r['effort'] = r.get('effort', 'Medium')

        if not scan_results:
            return jsonify({"status": "no_issues", "message": "No deprecated APIs detected."})

        # Process results
        detection = scan_results[0]
        input_data = {
            "old_usage": detection.get("api_name", "Legacy Pattern"),
            "new_api": detection.get("replacement", "Modern Standard"),
            "reason": detection.get("reason", "Deprecated pattern"),
            "code_snippet": code[:500] if not repo_url else f"Found in {detection['file']}"
        }
        
        ai_result = openclaw_run(input_data)

        return jsonify({
            "status": "success",
            "scan_result": detection,
            "all_results": scan_results,
            "ai_result": ai_result
        })

    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

if __name__ == "__main__":
    app.run(debug=True, port=5000)