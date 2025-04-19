# tests/conftest.py

import os
import sys

# Insert the project root (one level up) at the front of sys.path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root not in sys.path:
    sys.path.insert(0, root)
