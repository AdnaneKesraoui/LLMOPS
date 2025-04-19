import json
import pytest
from src.utils import (
    clean_doc_text, strip_code_fences,
    is_valid_json, is_valid_oas
)

# A minimal JSON Schema for testing is_valid_oas
DUMMY_SCHEMA = {
    "type": "object",
    "properties": {"foo": {"type": "integer"}},
    "required": ["foo"]
}

def test_clean_doc_text():
    inp = "  Hello\n   world\t!"
    out = clean_doc_text(inp)
    assert out == "Hello world !"

def test_strip_code_fences():
    fenced = "```json\n{\"foo\":1}\n```"
    assert strip_code_fences(fenced) == '{"foo":1}'
    # also strips generic fences
    assert strip_code_fences("```hello```") == "hello"

def test_is_valid_json():
    assert is_valid_json('{"x": 2}')
    assert not is_valid_json("not a json")

def test_is_valid_oas_pass():
    valid = '{"foo": 42}'
    assert is_valid_oas(valid, DUMMY_SCHEMA)

def test_is_valid_oas_fail():
    invalid = '{"bar": 5}'
    assert not is_valid_oas(invalid, DUMMY_SCHEMA)
