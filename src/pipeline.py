import os
import sys

# Ensure src/ is on PYTHONPATH so we can import local modules
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.insert(0, script_dir)

from utils import strip_code_fences, find_all_docs, is_valid_json
from generation import generate_spec

# Configuration
DOCS_DIR = os.path.join(project_root, 'data', 'raw')
OUT_DIR = os.path.join(project_root, 'generated')


def process_docs():
    os.makedirs(OUT_DIR, exist_ok=True)
    docs = find_all_docs(DOCS_DIR)

    for idx, path in enumerate(docs, 1):
        print(f"[{idx}/{len(docs)}] Generating spec for {path}")
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()

        raw_spec = generate_spec(text)
        spec = strip_code_fences(raw_spec)

        # Quick JSON sanity check
        if not is_valid_json(spec):
            print(f"⚠️  Invalid JSON for {path}")

        # Save output
        fname = os.path.splitext(os.path.basename(path))[0] + '.json'
        out_path = os.path.join(OUT_DIR, fname)
        with open(out_path, 'w', encoding='utf-8') as fout:
            fout.write(spec)


if __name__ == '__main__':
    process_docs()
