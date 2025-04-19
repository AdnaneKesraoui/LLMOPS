import os
import re
import json
import jsonschema
import subprocess
from tempfile import NamedTemporaryFile
from typing import List, Tuple, Any

def clean_doc_text(text: str) -> str:
    """
    Collapse any whitespace (newlines, multiple spaces) into single spaces,
    and trim leading/trailing whitespace.
    """
    return re.sub(r"\s+", " ", text).strip()

def strip_code_fences(text: str) -> str:
    """
    Remove leading/trailing Markdown ``` or ```json fences from a generated block.
    """
    t = re.sub(r"^\s*```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    return re.sub(r"\s*```\s*$", "", t)

def is_valid_json(text: str) -> bool:
    """Return True if `text` parses as JSON."""
    try:
        json.loads(text)
        return True
    except json.JSONDecodeError:
        return False

def is_valid_oas(text: str, schema: dict) -> bool:
    """
    Return True if `text` parses as JSON and validates against the given
    OpenAPI JSON Schema `schema`.
    """
    try:
        candidate = json.loads(text)
        jsonschema.validate(candidate, schema)
        return True
    except Exception:
        return False

def find_all_docs(directory: str) -> List[str]:
    """
    Walk `directory` recursively and return a list of all file paths.
    """
    docs: List[str] = []
    for root, _, files in os.walk(directory):
        for fname in files:
            docs.append(os.path.join(root, fname))
    return docs

def run_oasdiff(
    expected_spec: str,
    generated_spec: str,
    oasdiff_path: str
) -> Tuple[float, int, Any]:
    """
    Compare two OAS JSON strings using an external `oasdiff` tool at `oasdiff_path`.
    Returns:
      - correctness (1.0 if identical, else 0.0)
      - diff_count (number of differences, or -1 on error)
      - raw differences object (list or dict)
    """
    # Write both specs to temp files
    with NamedTemporaryFile("w", delete=False, suffix=".json", encoding="utf-8") as f1:
        f1.write(expected_spec)
        path1 = f1.name
    with NamedTemporaryFile("w", delete=False, suffix=".json", encoding="utf-8") as f2:
        f2.write(generated_spec)
        path2 = f2.name

    try:
        proc = subprocess.run(
            [oasdiff_path, "diff", path1, path2, "-f", "json"],
            capture_output=True, text=True, check=False
        )
        if not proc.stdout:
            return 0.0, -1, []
        diff_json = json.loads(proc.stdout)
        diffs = diff_json.get("differences", [])
        correctness = 1.0 if proc.returncode == 0 else 0.0
        return correctness, len(diffs), diffs
    except Exception:
        return 0.0, -1, []
    finally:
        os.remove(path1)
        os.remove(path2)
