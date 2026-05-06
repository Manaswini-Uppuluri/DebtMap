# Skill: migrate_deprecated_api

## Description
This skill analyzes deprecated API usage and provides migration guidance.

## Input
- old_usage: deprecated API call
- new_api: recommended replacement
- reason: why the API is deprecated
- code_snippet: original code

## Behavior
- Explain why the API is deprecated (1–2 sentences)
- Provide exactly 3 migration steps
- Rewrite the code using the new API
- Keep changes minimal and relevant

## Output (JSON)
{
  "explanation": "...",
  "migration_steps": ["...", "...", "..."],
  "updated_code": "..."
}