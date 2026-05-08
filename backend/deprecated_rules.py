DEPRECATED_RULES = [
    {
        "pattern": r"openai\.api_key\s*=",
        "api_name": "openai.api_key",
        "reason": "Direct assignment of api_key is deprecated in OpenAI v1.0.0+.",
        "replacement": "Use the OpenAI(api_key=...) client constructor instead.",
        "effort": "Low",
        "cost_per_occurrence": 10
    },
    {
        "pattern": r"eval\(",
        "api_name": "Insecure eval()",
        "reason": "The use of eval() is a major security risk and should be avoided.",
        "replacement": "Use ast.literal_eval() or a safer parsing method.",
        "effort": "High",
        "cost_per_occurrence": 100
    },
    {
        "pattern": r"os\.system\(",
        "api_name": "Legacy os.system",
        "reason": "os.system is deprecated for complex command execution.",
        "replacement": "Use the subprocess module instead.",
        "effort": "Medium",
        "cost_per_occurrence": 50
    },
    {
        "pattern": r"import\s+cgi",
        "api_name": "cgi module",
        "reason": "The 'cgi' module is deprecated in Python 3.11.",
        "replacement": "Use 'html' or 'multipart' instead.",
        "effort": "Medium",
        "cost_per_occurrence": 40
    },
    {
        "pattern": r"import\s+imp",
        "api_name": "imp module",
        "reason": "The 'imp' module is deprecated. Use 'importlib' instead.",
        "replacement": "import importlib",
        "effort": "Low",
        "cost_per_occurrence": 15
    }
]
