import os
import json
import pytest

from src.pipeline import process_docs
import src.generation as generation_module

# Paths
SMOKE_IN  = os.path.join("data", "raw", "smoke.txt")
SMOKE_OUT = os.path.join("generated", "smoke.json")

@pytest.fixture(autouse=True)
def cleanup_smoke():
    # Clean up before and after test
    if os.path.exists(SMOKE_OUT):
        os.remove(SMOKE_OUT)
    yield
    if os.path.exists(SMOKE_OUT):
        os.remove(SMOKE_OUT)


def test_pipeline_smoke(monkeypatch):
    # Monkey-patch generate_spec to avoid heavy model call
    monkeypatch.setattr(
        generation_module,
        "generate_spec",
        lambda txt: '{"openapi":"3.0.3","info":{"title":"Smoke","version":"1.0.0"},"paths":{}}'
    )

    # Ensure input file exists
    assert os.path.exists(SMOKE_IN), f"Smoke input not found: {SMOKE_IN}"

    # Run the pipeline
    process_docs()

    # Check output
    assert os.path.exists(SMOKE_OUT), "Pipeline did not create smoke.json"
    with open(SMOKE_OUT, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert data.get("openapi", "").startswith("3.0"), "Output JSON missing 'openapi' field"
