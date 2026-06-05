import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLI_PATH = PROJECT_ROOT / "src" / "cli.js"


def generate_structure(model_type: str, credits: int) -> dict:
    """
    Invoke the Node.js model factory CLI and return the parsed JSON result.

    Raises:
        RuntimeError: When the Node process fails or returns invalid JSON.
    """
    payload = json.dumps({"modelType": model_type, "credits": credits})

    try:
        result = subprocess.run(
            ["node", str(CLI_PATH)],
            input=payload,
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Node.js is not installed or not available on PATH."
        ) from exc

    stdout = result.stdout.strip()

    if not stdout:
        stderr = result.stderr.strip() or "No output from model generator."
        raise RuntimeError(stderr)

    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON from model generator: {stdout}") from exc

    return parsed
