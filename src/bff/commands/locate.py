import os

from bff.core.hash import hash_file
from bff.core.index_manager import load_index


def locate_command(target_filepath: str) -> None:
    """
    Checks if the content of an external file exists in the BFF index.
    """
    if not os.path.exists(target_filepath):
        print(f"Error: File '{target_filepath}' not found.")
        return

    if os.path.isdir(target_filepath):
        print(f"Error: '{target_filepath}' is a directory. Please specify a file.")
        return

    print(f"bff: Analyzing signature of '{target_filepath}'...")

    try:
        # Calculate hash of the external file
        target_hash = hash_file(target_filepath)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    index = load_index()
    entry = index.get(target_hash)

    if entry:
        paths = entry.get("paths", [])
        count = len(paths)
        print(f"Match found: This content exists {count} time(s) in the repository.")
        print("Locations:")
        for path in paths:
            print(f" - {path}")
    else:
        print("No match: This content is unique and not present in the index.")
