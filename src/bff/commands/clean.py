import os
from typing import List, Optional

from bff.core.constants import BFF_DIR
from bff.core.filtering import IndexFilters, should_index
from bff.core.index_manager import load_index, save_index


def _remove_file(filepath: str) -> bool:
    try:
        os.remove(filepath)
        return True
    except OSError as e:
        print(f"Error deleting {filepath}: {e}")
        return False


def _create_symlink(target: str, link_name: str) -> None:
    try:
        # Symlink requires absolute paths to be safe across directories
        if os.path.exists(link_name):
            os.remove(link_name)  # Ensure we don't fail if file exists
        os.symlink(os.path.abspath(target), link_name)
    except OSError as e:
        print(f"Error creating symlink {link_name}: {e}")


def clean_command(
    use_symlinks: bool = False, filters: Optional[IndexFilters] = None
) -> None:
    if not os.path.exists(BFF_DIR):
        print("Error: Not a bff repository.")
        return

    print(
        f"bff: Cleaning duplicates (Mode: {'Symlink' if use_symlinks else 'Delete'})..."
    )

    index = load_index()
    cleaned_count = 0
    bytes_saved = 0

    # Iterate over a copy of items because we might modify entries
    for file_hash, entry in index.items():
        paths: List[str] = entry.get("paths", [])

        if len(paths) <= 1:
            continue

        master_path = paths[0]

        if filters:
            if not should_index(master_path, filters):
                continue

        if not os.path.exists(master_path):
            print(f"Warning: Master file missing for {file_hash[:8]}, skipping...")
            continue

        duplicates = paths[1:]
        file_size = entry.get("size", 0)

        processed_dupes = []

        for dup_path in duplicates:
            # Safety check: ensure we don't process if it's already a link (unless we want to re-link)
            if os.path.exists(dup_path) and not os.path.islink(dup_path):
                if _remove_file(dup_path):
                    if use_symlinks:
                        _create_symlink(master_path, dup_path)
                        print(f"Linked: {dup_path} -> {master_path}")
                        cleaned_count += 1
                    else:
                        print(f"Deleted: {dup_path}")
                        bytes_saved += file_size
                        cleaned_count += 1
                else:
                    # Deletion failed, keep in index
                    processed_dupes.append(dup_path)

            elif os.path.islink(dup_path):
                # Currently, we skip existing symlinks to avoid loops or double processing
                # But we keep them in the index structure
                processed_dupes.append(dup_path)

            else:
                # File does not exist anymore, do not add back to processed_dupes
                pass

        # Update index: The entry now only contains the master + failed deletions + existing links
        index[file_hash]["paths"] = [master_path] + processed_dupes

    save_index(index)

    mb_saved = bytes_saved / (1024 * 1024)
    print(f"bff: Clean complete. Processed {cleaned_count} files.")
    if not use_symlinks:
        print(f"bff: Space reclaimed: {mb_saved:.2f} MB")
