import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = None

if GROQ_API_KEY:
    try:
        client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
    except:
        pass

def run_agent(data):
    """
    Returns specific technical advice for the detected pattern.
    """
    # Better Local Advice if AI is offline
    advice_map = {
        "openai.api_key": {
            "explanation": "OpenAI v1.0.0+ requires a client-based approach for thread safety and multiple environment handling.",
            "steps": ["Initialize 'client = OpenAI()'", "Remove global api_key assignments", "Pass API key to constructor"]
        },
        "openai.Completion.create": {
            "explanation": "The legacy Completions API is no longer optimized. Modern models use the ChatCompletions endpoint.",
            "steps": ["Change endpoint to 'client.chat.completions.create'", "Format input as 'messages' list", "Update response parsing logic"]
        },
        "os.system": {
            "explanation": "os.system is a legacy way to run commands that doesn't capture output and is prone to shell injection.",
            "steps": ["Import 'subprocess'", "Use 'subprocess.run' or 'subprocess.Popen'", "Properly escape arguments in a list"]
        }
    }

    pattern = data.get("old_usage", "")
    local_advice = advice_map.get(pattern, {
        "explanation": f"Architectural shift required for {pattern}. This legacy pattern is deprecated and may lead to performance bottlenecks.",
        "steps": ["Locate all references in codebase", "Replace with modern standard suggested", "Run regression tests"]
    })

    if not client:
        return {
            "agent_type": "Local Engine",
            "explanation": local_advice["explanation"],
            "migration_steps": local_advice["steps"],
            "updated_code": "Local modernization logic applied.",
            "is_mock": True
        }

    try:
        # Ask for explanation, steps, and updated code
        prompt = f"""
        Explain why {data['old_usage']} is deprecated and how to move to {data['new_api']} in 2 sentences.
        Original Code: {data['code_snippet']}
        
        Provide:
        1. A brief explanation.
        2. Exactly 3 migration steps.
        3. The modernized code snippet.
        """
        
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "agent_type": "Neural AI",
            "explanation": completion.choices[0].message.content,
            "migration_steps": local_advice["steps"],
            "updated_code": f"# Modernized using {data['new_api']}\n{data['code_snippet'].replace(data['old_usage'], data['new_api'])}",
            "is_mock": False
        }
    except:
        return {
            "agent_type": "Local Engine Fallback",
            "explanation": local_advice["explanation"],
            "migration_steps": local_advice["steps"],
            "updated_code": "Manual replacement required.",
            "is_mock": True
        }