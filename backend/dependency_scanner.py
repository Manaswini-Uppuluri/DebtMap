import json
import re
import urllib.request
from typing import List, Dict, Any

def check_npm_package(package_name: str) -> Dict[str, Any]:
    """Queries the npm registry to see if a JavaScript package is deprecated."""
    url = f"https://registry.npmjs.org/{package_name}/latest"
    try:
        # We add a User-Agent header as some APIs block generic requests
        req = urllib.request.Request(url, headers={'User-Agent': 'DebtMap-Scanner/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
            # The npm registry explicitly includes a "deprecated" field if the author marked it as such
            if "deprecated" in data:
                return {
                    "api_name": package_name,
                    "ecosystem": "npm",
                    "is_deprecated": True,
                    "reason": data["deprecated"],
                    "replacement": "Check npm registry for modern alternatives.",
                    "effort": "high",  # Replacing an entire package is usually a high effort task
                    "estimated_cost": 100 # Arbitrary high cost for package replacement
                }
    except Exception:
        pass # Ignore network errors or missing packages for the MVP
        
    return {"is_deprecated": False}

def check_pypi_package(package_name: str) -> Dict[str, Any]:
    """Queries the PyPI registry to see if a Python package is yanked or deprecated."""
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'DebtMap-Scanner/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            info = data.get("info", {})
            
            # PyPI uses "yanked" to indicate a release was pulled back.
            yanked = info.get("yanked", False)
            yanked_reason = info.get("yanked_reason") or "No reason provided."
            summary = info.get("summary", "").lower()
            
            # PyPI doesn't have a strict 'deprecated' field like npm, so we check 'yanked' 
            # or simply look for the word "deprecated" in the package's summary description.
            is_deprecated = yanked or "deprecated" in summary
            reason = yanked_reason if yanked else ("Package summary indicates deprecation." if "deprecated" in summary else "")
            
            if is_deprecated:
                return {
                    "api_name": package_name,
                    "ecosystem": "pypi",
                    "is_deprecated": True,
                    "reason": reason,
                    "replacement": "Check PyPI for modern alternatives.",
                    "effort": "high",
                    "estimated_cost": 100
                }
    except Exception:
        pass
        
    return {"is_deprecated": False}

def scan_package_json(content: str) -> List[Dict[str, Any]]:
    """Parses package.json content and checks all dependencies against npm."""
    results = []
    try:
        data = json.loads(content)
        # Combine dependencies and devDependencies
        deps = list(data.get("dependencies", {}).keys()) + list(data.get("devDependencies", {}).keys())
        
        for dep in deps:
            res = check_npm_package(dep)
            if res.get("is_deprecated"):
                del res["is_deprecated"] # Clean up our internal flag before returning
                results.append(res)
    except json.JSONDecodeError:
        pass
    return results

def scan_requirements_txt(content: str) -> List[Dict[str, Any]]:
    """Parses requirements.txt content and checks all dependencies against PyPI."""
    results = []
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        # Ignore comments and empty lines
        if not line or line.startswith('#'):
            continue
            
        # Extract the base package name (ignore versions like ==1.0.0, >=2.0)
        match = re.match(r'^([a-zA-Z0-9_\-]+)', line)
        if match:
            pkg_name = match.group(1)
            res = check_pypi_package(pkg_name)
            if res.get("is_deprecated"):
                del res["is_deprecated"]
                results.append(res)
    return results

if __name__ == "__main__":
    # --- Quick Tests ---
    
    print("--- 1. Testing npm (package.json) ---")
    # We include 'request', which is famously deprecated in the Node ecosystem.
    mock_package_json = '''
    {
      "dependencies": {
        "express": "^4.17.1",
        "request": "^2.88.2" 
      }
    }
    '''
    npm_results = scan_package_json(mock_package_json)
    print(json.dumps(npm_results, indent=4))
    
    print("\n--- 2. Testing PyPI (requirements.txt) ---")
    # We include 'django-rest-swagger', which is deprecated.
    mock_requirements = '''
    flask==2.0.1
    django-rest-swagger
    '''
    pypi_results = scan_requirements_txt(mock_requirements)
    print(json.dumps(pypi_results, indent=4))
