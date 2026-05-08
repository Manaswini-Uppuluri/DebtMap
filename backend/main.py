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
    for root, dirs, files in os.walk(directory_path):
        # Skip git and hidden folders
        if '.git' in dirs: dirs.remove('.git')
        
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.go')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        findings = scan_code(content)
                        for finding in findings:
                            finding['file'] = os.path.relpath(file_path, directory_path)
                            all_findings.append(finding)
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")
    return all_findings

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "API running"})

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    code = data.get("code", "")
    repo_url = data.get("repo_url", "")

    # Create a temp directory for scanning
    temp_dir = tempfile.mkdtemp()
    
    try:
        scan_results = []
        
        if repo_url:
            # Step 1: Clone Repo
            print(f"DEBUG: Starting clone of {repo_url} into {temp_dir}")
            try:
                # Use git.exe explicitly and handle as a shell command for Windows stability
                result = subprocess.run(
                    f'git clone --depth 1 "{repo_url}" "{temp_dir}"', 
                    capture_output=True, 
                    text=True, 
                    shell=True
                )
                if result.returncode != 0:
                    print(f"DEBUG: Git Clone Failed: {result.stderr}")
                    return jsonify({"status": "error", "message": f"Git Clone Failed: {result.stderr}"}), 500
                
                print("DEBUG: Clone successful. Starting directory scan...")
                scan_results = scan_directory(temp_dir)
                print(f"DEBUG: Scan complete. Found {len(scan_results)} issues.")
            except Exception as clone_err:
                print(f"DEBUG: Subprocess Error: {clone_err}")
                return jsonify({"status": "error", "message": f"Internal Error: {str(clone_err)}"}), 500
        elif code:
            # Step 1: Scan raw code
            scan_results = scan_code(code)
            for r in scan_results:
                r['file'] = "source_input"
        else:
            return jsonify({"error": "No code or repo_url provided"}), 400

        if not scan_results:
            return jsonify({
                "status": "no_issues",
                "message": "No deprecated APIs found"
            })

        # Calculate Summary Metrics
        total_cost = sum(r.get('estimated_cost', 0) for r in scan_results)
        unique_files = len(set(r.get('file', 'unknown') for r in scan_results))
        
        # Sort by cost descending
        scan_results.sort(key=lambda x: x.get('estimated_cost', 0), reverse=True)

        return jsonify({
            "status": "success",
            "all_results": scan_results,
            "summary": {
                "total_cost": total_cost,
                "total_files": unique_files
            }
        })

    except Exception as e:
        print(f"Error during analysis: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        # Clean up
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    app.run(debug=True, port=5000)