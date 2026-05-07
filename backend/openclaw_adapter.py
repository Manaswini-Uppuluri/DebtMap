from agent import run_agent

def openclaw_run(input_data):
    """
    OpenClaw-style execution wrapper
    """

    result = run_agent(input_data)

    return {
        "agent": "openclaw-style",
        "status": "success",
        "data": result
    }