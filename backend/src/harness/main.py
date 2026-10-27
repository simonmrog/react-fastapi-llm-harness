import subprocess
import sys
from anthropic import Anthropic

from harness import config
from harness.logger import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)
client = Anthropic()

def execute_python_code(code_string):
    logger.info("[Harness] Executing code in sandbox...")
    try:
        result = subprocess.run(
            [sys.executable, "-c", code_string],
            capture_output=True,
            text=True,
            timeout=config.EXECUTION_TIMEOUT,
            check=False
        )
        if result.returncode == 0:
            return {"success": True, "output": result.stdout}

        return {"success": False, "output": result.stderr}
    except Exception as e:
        return {"success": False, "output": str(e)}

def run_autonomous_agent():
    task = (
        "Write a python script that extracts all numbers from this string: "
        "'Total: 45 units, Price: $120, Tax: 15' and calculates their total sum. Print only the final sum."
    )

    system_instruction = (
        "You are an autonomous coding agent. Your goal is to solve the user's task by writing executable Python code. "
        "CRITICAL: Output ONLY valid, executable Python code. "
        "Do not include markdown blocks (no ```python), do not explain anything, do not write prose. "
        "If you receive an error log from a previous run, use it to fix your code and output the corrected script."
    )

    messages = [{"role": "user", "content": task}]
    max_iterations = config.MAX_ITERATIONS

    logger.info("[Harness] Starting Agent Mission: %s", task)

    for turn in range(1, max_iterations + 1):
        logger.info("--- Iteration %d/%d ---", turn, max_iterations)
        logger.info("[Harness] Querying Claude...")

        # Call the Anthropic API
        response = client.messages.create(
            model=config.MODEL,
            max_tokens=config.MAX_TOKENS,
            thinking={"type": "adaptive", "display": "summarized"},
            system=system_instruction,
            messages=messages
        )

        for block in response.content:
            if block.type == "thinking":
                logger.info("Thinking: %s", block.thinking.strip())
            elif block.type == "text":
                logger.info("[Claude Proposed Code]:\n%s", block.text)

        suggested_code = "".join(
            block.text for block in response.content if block.type == "text"
        ).strip()

        # Harness intercepts and runs it inside the isolated environment
        execution = execute_python_code(suggested_code)

        if execution["success"]:
            logger.info("[Harness] Goal achieved successfully!")
            logger.info("[Harness] Final Console Output:\n%s", execution['output'].strip())
            break
        else:
            logger.error("[Harness] Code execution failed.")
            logger.error("[Harness]:\n%s", execution['output'].strip())

            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": f"Your previous code failed with the following execution error:\n{execution['output']}\nFix the error and provide the updated complete code script."
            })

    else:
        logger.error("[Harness] Mission failed. Max iterations reached without success.")


if __name__ == "__main__":
    run_autonomous_agent()
