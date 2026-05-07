import os
import sys
import json
import tempfile
import subprocess
import shutil
import argparse

from flask import Flask, request, jsonify
from flask_cors import CORS
try:
    from openclaw_adapter import openclaw_run
except ImportError:
    # Fallback if openclaw_adapter is not yet available
    def openclaw_run(data):
        return {"error": "openclaw_adapter module not found", "data": data}

# Import the two detection engines we built
from scanner import scan_code
from dependency_scanner import scan_package_json, scan_requirements_txt

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "API running"})

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    code = data.get("code", "")
    repo_url = data.get("repo_url", "")

    if not code and not repo_url:
        return jsonify({"error": "No code or repository URL provided"}), 400

    try:
        final_results = []

        if code:
            # Step 1: scan code
            scan_results = scan_code(code)
            if not scan_results:
                return jsonify({
                    "status": "no_issues",
                    "message": "No deprecated APIs found"
                })
            
            # For direct code input, we still take the first issue for AI result if needed,
            # but we return the whole scan for the dashboard.
            final_results = scan_results
            
            # Step 3: AI agent for the first result (legacy compatibility)
            # You can expand this to loop through results if you want AI for all
            detection = scan_results[0]
            input_data = {
                "old_usage": detection.get("old_usage", "unknown"),
                "new_api": detection.get("new_api", "unknown"),
                "reason": detection.get("reason", "Not specified"),
                "code_snippet": code
            }
            ai_result = openclaw_run(input_data)
            
            return jsonify({
                "status": "success",
                "scan_result": detection, # Legacy single result for older UI parts
                "all_results": final_results, # Full list for the new dashboard
                "ai_result": ai_result
            })

        elif repo_url:
            # Handle Repository Scanning
            temp_dir = tempfile.mkdtemp(prefix="debtmap_api_")
            try:
                success, error_msg = clone_repository(repo_url, temp_dir)
                if success:
                    final_results = scan_directory(temp_dir, False) # auto_fix=False for API
                    
                    if not final_results:
                         return jsonify({
                            "status": "no_issues",
                            "message": "No issues found in this repository."
                        })
                        
                    return jsonify({
                        "status": "success",
                        "all_results": final_results,
                        "repo_mode": True
                    })
                else:
                    return jsonify({"status": "error", "message": f"Clone Error: {error_msg}"}), 500
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


def clone_repository(repo_url: str, dest_dir: str):
    """Clones a git repository into the specified directory."""
    print(f"[*] Cloning {repo_url} into {dest_dir}...")
    try:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, dest_dir],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"[*] Clone successful. Directory contents: {os.listdir(dest_dir)}")
        return True, ""
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        print(f"[!] Failed to clone repository: {error_msg}")
        return False, error_msg
    except FileNotFoundError:
        error_msg = "Git is not installed or not in the system PATH."
        print(f"[!] {error_msg}")
        return False, error_msg

def scan_directory(directory: str, auto_fix: bool = False) -> list:
    """Walks through a directory, reads files, and passes them to the detection engines."""
    all_findings = []
    print(f"[*] Scanning directory: {directory}")
    
    file_count = 0
    for root, _, files in os.walk(directory):
        # Skip git metadata folders to speed up processing
        if '.git' in root:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            # Create a clean relative path to display in the final JSON
            rel_path = os.path.relpath(file_path, directory)
            
            # Debug: print every file we look at
            print(f"[*] Checking file: {rel_path}")
            file_count += 1
            
            try:
                # 1. Route Dependency Files to the Dependency Scanner
                if file == "package.json":
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        results = scan_package_json(content)
                        for r in results:
                            r["file"] = rel_path
                            all_findings.append(r)
                            
                elif file == "requirements.txt":
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        results = scan_requirements_txt(content)
                        for r in results:
                            r["file"] = rel_path
                            all_findings.append(r)
                            
                # 2. Route Source Code Files to the Regex Scanner
                elif file.endswith((".py", ".js")):
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    results = scan_code(content)
                    
                    if auto_fix and results:
                        file_modified = False
                        lines = content.split('\n')
                        for r in results:
                            for occ in r.get("occurrences", []):
                                if occ.get("suggested_code") is not None:
                                    line_idx = occ["line_number"] - 1
                                    lines[line_idx] = occ["suggested_code"]
                                    file_modified = True
                                    occ["status"] = "fixed"
                                else:
                                    occ["status"] = "manual_intervention_required"
                                    
                        if file_modified:
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write('\n'.join(lines))
                            print(f"[*] Applied auto-fixes to {rel_path}")

                    for r in results:
                        r["file"] = rel_path
                        r["full_content"] = content
                        all_findings.append(r)
                            
            except Exception:
                # Silently ignore files that can't be read (e.g. binary files with .js extensions, weird encodings)
                pass
                
    print(f"[*] Finished scan. Total files checked: {file_count}")
    return all_findings

def main():
    parser = argparse.ArgumentParser(description="DebtMap Detection Engine Controller")
    # Make target optional by using nargs="?"
    parser.add_argument("target", nargs="?", help="GitHub repository URL (https://...) OR a local directory path. Omit to run the API server.")
    parser.add_argument("--fix", action="store_true", help="Automatically apply suggested code replacements where possible")
    parser.add_argument("--serve", action="store_true", help="Run the Flask API server")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the API server on")
    args = parser.parse_args()

    # If --serve is passed or no target is provided, we run the Flask server
    if args.serve or not args.target:
        print(f"[*] Starting API server on port {args.port}...")
        app.run(debug=True, port=args.port)
        return

    target = args.target
    is_url = target.startswith("http://") or target.startswith("https://")
    
    final_results = []
    
    if is_url:
        # Create a temporary directory for cloning
        temp_dir = tempfile.mkdtemp(prefix="debtmap_")
        try:
            if clone_repository(target, temp_dir):
                final_results = scan_directory(temp_dir, args.fix)
        finally:
            print(f"[*] Cleaning up temporary directory...")
            # We use ignore_errors=True to handle occasional Windows permission locks
            shutil.rmtree(temp_dir, ignore_errors=True)
    else:
        # Assume it's a local directory path or file
        if os.path.isdir(target):
            final_results = scan_directory(target, args.fix)
        elif os.path.isfile(target):
            file_path = target
            rel_path = os.path.basename(file_path)
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            results = scan_code(content)
            if args.fix and results:
                file_modified = False
                lines = content.split('\n')
                for r in results:
                    for occ in r.get("occurrences", []):
                        if occ.get("suggested_code") is not None:
                            line_idx = occ["line_number"] - 1
                            lines[line_idx] = occ["suggested_code"]
                            file_modified = True
                            occ["status"] = "fixed"
                        else:
                            occ["status"] = "manual_intervention_required"
                            
                if file_modified:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write('\n'.join(lines))
                    print(f"[*] Applied auto-fixes to {rel_path}")

            for r in results:
                r["file"] = rel_path
                final_results.append(r)
        else:
            print(f"[!] Error: '{target}' is not a valid local directory, file, or URL.")
            sys.exit(1)
            
    # Output the massive unified JSON for the AI Layer
    print("\n--- DETECTION ENGINE FINAL RESULTS ---")
    print(json.dumps(final_results, indent=4))

if __name__ == "__main__":
    main()
