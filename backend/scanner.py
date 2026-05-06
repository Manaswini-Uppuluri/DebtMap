import re
import json
from typing import List, Dict, Any
from deprecated_rules import DEPRECATED_RULES

def _is_comment(line: str) -> bool:
    """
    Check if a given line is a simple comment.
    
    Args:
        line (str): The code line to check.
        
    Returns:
        bool: True if the line starts with a comment symbol, False otherwise.
    """
    stripped = line.strip()
    return stripped.startswith('#') or stripped.startswith('//')

def scan_code(code: str) -> List[Dict[str, Any]]:
    """
    Scans the input code for deprecated APIs using predefined rules.
    
    Args:
        code (str): The source code to scan.
        
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing detected APIs,
                              effort, cost estimates, and exact line matches.
    """
    lines = code.split('\n')
    results: Dict[str, Dict[str, Any]] = {}
    
    compiled_rules = [
        {"rule": rule, "regex": re.compile(rule["pattern"])} 
        for rule in DEPRECATED_RULES
    ]
        
    for line_num, line in enumerate(lines, start=1):
        if _is_comment(line):
            continue
            
        for compiled in compiled_rules:
            rule = compiled["rule"]
            regex = compiled["regex"]
            
            if regex.search(line):
                api_name = rule["api_name"]
                
                if api_name not in results:
                    results[api_name] = {
                        "api_name": api_name,
                        "reason": rule["reason"],
                        "replacement": rule["replacement"],
                        "manual_steps": rule.get("manual_steps", "Manual migration required."),
                        "occurrences": [],
                        "effort": rule["effort"],
                        "cost_per_occurrence": rule["cost_per_occurrence"]
                    }
                
                suggested_code = None
                if "replace_pattern" in rule:
                    suggested_code = regex.sub(rule["replace_pattern"], line)
                
                results[api_name]["occurrences"].append({
                    "line_number": line_num,
                    "original_code": line,
                    "suggested_code": suggested_code
                })
                
    final_results = []
    for api_name, data in results.items():
        data["estimated_cost"] = len(data["occurrences"]) * data["cost_per_occurrence"]
        del data["cost_per_occurrence"]
        final_results.append(data)
        
    return final_results

if __name__ == "__main__":
    # Small test example
    sample_code = """import optparse
# This is a comment containing document.execCommand()
def main():
    parser = optparse.OptionParser()
    escaped = escape("some text")
    // Use window.showModalDialog() later
    window.showModalDialog('test.html')
"""
    
    findings = scan_code(sample_code)
    print(json.dumps(findings, indent=4))
