import os
import json
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Groq client
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Safe base directory (prevents path bugs)
BASE_DIR = Path(__file__).resolve().parent

def load_openclaw():
    soul = (BASE_DIR / "SOUL.md").read_text()
    skill = (BASE_DIR / "SKILL.md").read_text()
    beat = (BASE_DIR / "HEARTBEAT.md").read_text()
    return f"{soul}\n\n{skill}\n\n{beat}"

def run_agent(detection_item: dict) -> dict:
    system_prompt = load_openclaw()

    user_message = f"""
You are a migration assistant.

Explain clearly WHY the API is deprecated in 1-2 sentences.

Then provide exactly 3 migration steps.

Then rewrite the code using the new API.

old_usage: {detection_item['old_usage']}
new_api: {detection_item['new_api']}
reason: {detection_item['reason']}
code_snippet: {detection_item['code_snippet']}

Return ONLY valid JSON:
{{
  "explanation": "...",
  "migration_steps": ["...", "...", "..."],
  "updated_code": "..."
}}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.2
    )

    raw = response.choices[0].message.content.strip()

    # Clean formatting
    raw = raw.replace("```json", "").replace("```", "").strip()

    # ✅ Safe JSON parsing
    try:
        result = json.loads(raw)
    except:
        result = {
            "explanation": "Parsing error",
            "migration_steps": ["Check API docs", "Update method", "Test code"],
            "updated_code": detection_item["code_snippet"]
        }

    # ✅ MEMORY UPDATE (correct place)
    try:
        with open(BASE_DIR / "HEARTBEAT.md", "a") as f:
            f.write(f"\nMigrated: {detection_item['old_usage']} -> {detection_item['new_api']}")
    except:
        pass  # don't break system if memory fails

    return result