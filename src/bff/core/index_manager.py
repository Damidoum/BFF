import json
import os
import threading
from typing import Any, Dict, Optional

import magic

from bff.core.constants import BFF_DIR, INDEX_FILE

# Global lock for thread-safe operations if needed,
# though file operations themselves are not atomic without strict locking.
_LOCK = threading.Lock()


def load_index(index_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load the index from disk.

    Args:
        index_path: Optional path to the index file. Defaults to global constant.

    Returns:
        Dict containing the index data. Returns empty dict if file doesn't exist
        or is corrupted.
    """
    path = index_path or INDEX_FILE
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_index(index_data: Dict[str, Any], index_path: Optional[str] = None) -> None:
    """
    Save the index to disk atomically.

    Args:
        index_data: Dictionary containing the index data to save.
        index_path: Optional path to the index file. Defaults to global constant.
    """
    target_path = index_path or INDEX_FILE
    temp_file = target_path + ".tmp"

    # Ensure directory exists
    os.makedirs(os.path.dirname(target_path), exist_ok=True)

    with open(temp_file, "w") as f:
        json.dump(index_data, f, indent=4)
    os.replace(temp_file, target_path)


def get_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract metadata for a given file.

    Args:
        filepath: Absolute path to the file.

    Returns:
        Dict containing size, mimetype, created_at, and mtime.
    """
    try:
        mime = magic.from_file(filepath, mime=True)
    except Exception:
        mime = "unknown"

    stat = os.stat(filepath)
    return {
        "size": stat.st_size,
        "mimetype": mime,
        "created_at": stat.st_ctime,
        "mtime": stat.st_mtime,
    }


def find_repository_root() -> Optional[str]:
    """
    Traverses up the directory tree to find the folder containing .bff/.

    Returns:
        Absolute path to the repository root, or None if not found.
    """
    current_dir = os.path.abspath(os.getcwd())
    while True:
        if os.path.exists(os.path.join(current_dir, BFF_DIR)):
            return current_dir
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            return None
        current_dir = parent
