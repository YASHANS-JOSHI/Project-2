import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RULE_ENGINE_CLI_PATH = PROJECT_ROOT / "src" / "ruleEngineCli.js"


def generate_unit_themes(
    course_name: str,
    credits: int,
    model_type: str,
    units: list[dict],
) -> dict:
    """
    Invoke the Node.js Rule Engine CLI and return themed unit output.

    Raises:
        RuntimeError: When the Node process fails or returns invalid JSON.
    """
    payload = json.dumps(
        {
            "courseName": course_name,
            "credits": credits,
            "modelType": model_type,
            "units": units,
        }
    )

    try:
        result = subprocess.run(
            ["node", str(RULE_ENGINE_CLI_PATH)],
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
        stderr = result.stderr.strip() or "No output from Rule Engine."
        raise RuntimeError(stderr)

    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON from Rule Engine: {stdout}") from exc

    return parsed


def merge_structure_with_themes(structure: dict, themes: dict) -> dict:
    """Combine model structure output with Rule Engine theme output."""
    themed_units = themes.get("units", [])
    structure_units = structure.get("units", [])

    merged_units = []
    for structure_unit, themed_unit in zip(structure_units, themed_units):
        merged_units.append(
            {
                **structure_unit,
                "unitTitle": themed_unit.get("unitTitle"),
                "shortDescription": themed_unit.get("shortDescription"),
                "topics": structure_unit.get("topics", []),
                "topicCount": structure_unit.get(
                    "topicCount",
                    len(structure_unit.get("topics", [])),
                ),
            }
        )

    return {
        **structure,
        "courseName": themes.get("courseName", structure.get("courseName")),
        "units": merged_units,
        "warnings": structure.get("warnings", []),
        "enforcement": structure.get("enforcement", {}),
    }
