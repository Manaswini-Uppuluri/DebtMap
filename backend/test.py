from agent import run_agent

# Sample test input (matches your scanner output format)
test_input = {
    "old_usage": "openai.ChatCompletion.create",
    "new_api": "openai.chat.completions.create",
    "reason": "Removed in OpenAI SDK v1.0",
    "code_snippet": "response = openai.ChatCompletion.create(model='gpt-4', messages=msgs)"
}

try:
    result = run_agent(test_input)

    print("\n=== AI OUTPUT ===\n")
    print("Explanation:")
    print(result["explanation"])

    print("\nSteps:")
    for i, step in enumerate(result["migration_steps"], 1):
        print(f"{i}. {step}")

    print("\nUpdated Code:")
    print(result["updated_code"])

except Exception as e:
    print("\n❌ ERROR OCCURRED:\n")
    print(e)