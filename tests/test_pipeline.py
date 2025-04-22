import os
import json
import pytest

from pipeline import process_docs

SMOKE_IN  = os.path.join("data", "raw", "smoke.txt")
SMOKE_OUT = os.path.join("generated", "smoke.json")

@pytest.fixture(autouse=True)
def clean_smoke():
    # remove old output
    if os.path.exists(SMOKE_OUT):
        os.remove(SMOKE_OUT)
    yield
    if os.path.exists(SMOKE_OUT):
        os.remove(SMOKE_OUT)

def test_pipeline_smoke(monkeypatch):
    # stub out the heavy model call to a simple JSON return
    import generation
    monkeypatch.setattr(generation, "generate_spec", lambda txt: '{"openapi":"3.0.3","info":{"title":"Smoke","version":"1.0.0"},"paths":{}}')

    process_docs()

    assert os.path.exists(SMOKE_OUT), "Pipeline should write smoke.json"
    with open(SMOKE_OUT) as f:
        out = json.load(f)
    assert out["openapi"].startswith("3.0"), "Output JSON should have openapi field"
