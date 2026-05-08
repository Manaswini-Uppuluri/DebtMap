# HEARTBEAT.md — DebtMap Migration Advisor

## Trigger Condition
Activated when a developer submits code via POST /analyze

## Execution Steps
1. Receive code snippet or GitHub repo URL from frontend
2. Run scanner.py — detect deprecated APIs using regex rules
3. For each detected issue, call run_agent() with old_usage, new_api, reason, code_snippet
4. LLM generates explanation, 3 migration steps, and updated code
5. Append migration log entry to this file (memory persistence)
6. Return structured JSON report to frontend

## Memory Log