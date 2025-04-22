import os
import json
import pytest
from src.pipeline import process_docs

SMOKE_IN  = "data/raw/smoke.txt"
SMOKE_OUT = "generated/smoke.json"

@pytest.fixture(autouse=True)
def cleanup_smoke():
    # ensure output dir exists and is clean
    if os.path.exists(SMOKE_OUT):
        os.remove(SMOKE_OUT)
    yield
    if os.path.exists(SMOKE_OUT):
        os.remove(SMOKE_OUT)

def test_pipeline_smoke(monkeypatch):
    # Monkey‑patch generate_spec to return a known JSON
    import src.generation as gen_mod
    monkeypatch.setattr(gen_mod, "generate_spec", lambda txt: '{"openapi":"3.0.3","info":{"title":"Smoke","version":"1.0.0"},"paths":{}}')

    # Run processing
    process_docs()

    # Assert output file exists and is valid JSON
    assert os.path.exists(SMOKE_OUT)
    with open(SMOKE_OUT) as f:
        data = json.load(f)
    assert data["openapi"].startswith("3.0")
