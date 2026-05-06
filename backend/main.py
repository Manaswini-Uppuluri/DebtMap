import os
import sys
import json
import tempfile
import subprocess
import shutil
import argparse

# Import the two detection engines we built
from scanner import scan_code
from dependency_scanner import scan_package_json, scan_requirements_txt

def clone_repository(repo_url: str, dest_dir: str) -> bool:
    """Clones a git repository into the specified directory."""
    print(f"[*] Cloning {repo_url} into {dest_dir}...")
    try:
        subprocess.run(
            ["git", "clone", repo_url, dest_dir],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to clone repository: {e}")
        return False
    except FileNotFoundError:
        print("[!] Git is not installed or not in PATH.")
        return False

def scan_directory(directory: str, auto_fix: bool = False) -> list:
    """Walks through a directory, reads files, and passes them to the detection engines."""
    all_findings = []
    print(f"[*] Scanning directory: {directory}")
    
    for root, _, files in os.walk(directory):
        # Skip git metadata folders to speed up processing
        if '.git' in root:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            # Create a clean relative path to display in the final JSON
            rel_path = os.path.relpath(file_path, directory)
            
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
                        all_findings.append(r)
                            
            except Exception:
                # Silently ignore files that can't be read (e.g. binary files with .js extensions, weird encodings)
                pass
                
    return all_findings

def main():
    parser = argparse.ArgumentParser(description="DebtMap Detection Engine Controller")
    parser.add_argument("target", help="GitHub repository URL (https://...) OR a local directory path")
    parser.add_argument("--fix", action="store_true", help="Automatically apply suggested code replacements where possible")
    args = parser.parse_args()

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
            # Create a temporary directory to use scan_directory logic, or handle file directly
            # For simplicity, we can just run scan_directory on the parent folder but ONLY process this file.
            # Actually, it's simpler to just copy the file logic here:
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
