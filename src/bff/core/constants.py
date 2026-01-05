import os

BFF_DIR = ".bff"
INDEX_FILE = os.path.join(BFF_DIR, "index.json")
CONFIG_FILE = os.path.join(BFF_DIR, "config.json")
IGNORED_DIRS = {
    ".git",
    ".bff",
    "node_modules",
    "$RECYCLE.BIN",
    "__pycache__",
    ".venv",
    "venv",
}
