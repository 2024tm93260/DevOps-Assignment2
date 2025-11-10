import os, sys
# ensure repository root is on sys.path so "import app" works in tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
