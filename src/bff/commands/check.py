import os

from bff.core.constants import BFF_DIR
from bff.core.index_manager import load_index, save_index


def check_command(prune: bool = False) -> None:
    if not os.path.exists(BFF_DIR):
        print("Error: No bff repository found.")
        return

    print("bff: Checking index integrity...")
    index = load_index()

    missing_files = 0
    empty_entries = 0
    hashes_to_remove = []

    # Iterate over a list of keys since we might modify the dict
    for file_hash in list(index.keys()):
        data = index[file_hash]
        paths = data.get("paths", [])
        valid_paths = []

        # Check each path
        for path in paths:
            if os.path.exists(path):
                # Optional: Could also check if size matches to detect modification
                valid_paths.append(path)
            else:
                print(f"Missing: {path}")
                missing_files += 1

        if prune:
            # Update the entry with only valid paths
            if valid_paths:
                index[file_hash]["paths"] = valid_paths
            else:
                # No paths left for this content? Mark for deletion
                hashes_to_remove.append(file_hash)
                empty_entries += 1

    if prune:
        for h in hashes_to_remove:
            del index[h]

        save_index(index)
        print(
            f"bff: Check complete. Pruned {missing_files} missing paths and {empty_entries} empty entries."
        )
    else:
        print(f"bff: Check complete. Found {missing_files} missing files.")
        if missing_files > 0:
            print("Tip: Run 'bff check --prune' to clean the database.")
