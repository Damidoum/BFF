import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, Tuple

from tqdm import tqdm

from bff.core.constants import BFF_DIR, IGNORED_DIRS
from bff.core.filtering import IndexFilters, should_index
from bff.core.hash import hash_file
from bff.core.index_manager import (
    _LOCK,
    find_repository_root,
    get_metadata,
    load_index,
    save_index,
)


def _process_file_incremental(
    filepath: str,
    index: Dict[str, Any],
    filters: IndexFilters,
    cache_map: Dict[str, Tuple[float, int]],
) -> str:
    """
    Returns status: 'indexed', 'skipped', 'failed', 'ignored'.
    """
    # Use the shared filtering logic
    if not should_index(filepath, filters):
        return "ignored"

    try:
        abs_path = os.path.abspath(filepath)
        stat = os.stat(abs_path)

        # Incremental Optimization (Cache Check)
        if abs_path in cache_map:
            cached_mtime, cached_size = cache_map[abs_path]
            if (
                stat.st_size == cached_size
                and abs(stat.st_mtime - cached_mtime) < 0.001
            ):
                return "skipped"

        # Hashing
        file_hash = hash_file(abs_path)
        metadata = get_metadata(abs_path)

        with _LOCK:
            if file_hash not in index:
                index[file_hash] = {
                    "size": metadata["size"],
                    "mimetype": metadata["mimetype"],
                    "created_at": metadata["created_at"],
                    "mtime": metadata["mtime"],
                    "paths": [abs_path],
                }
            else:
                index[file_hash]["mtime"] = metadata["mtime"]
                if abs_path not in index[file_hash]["paths"]:
                    index[file_hash]["paths"].append(abs_path)

        return "indexed"

    except OSError:
        return "failed"


def index_command(filters: IndexFilters) -> None:
    root_dir = find_repository_root()
    if not root_dir:
        print("Error: No .bff repository found. Run 'init' inside the project.")
        return

    index_file_path = os.path.join(root_dir, BFF_DIR, "index.json")
    print(f"bff: Indexing root: {root_dir}")

    index = load_index(index_file_path)

    # Build lookup map: Path -> (Mtime, Size)
    path_cache = {}
    for entry in index.values():
        mtime = entry.get("mtime", 0.0)
        size = entry.get("size", 0)
        for p in entry.get("paths", []):
            path_cache[p] = (mtime, size)

    print("bff: Scanning file system...")
    all_files = []
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for f in files:
            full_path = os.path.join(root, f)
            if BFF_DIR in full_path:
                continue
            all_files.append(full_path)

    print(f"bff: Found {len(all_files)} candidates.")

    stats = {"indexed": 0, "skipped": 0, "failed": 0}
    seen_paths_on_disk = set()

    max_workers = min(32, (os.cpu_count() or 1) + 4)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_process_file_incremental, f, index, filters, path_cache): f
            for f in all_files
        }

        with tqdm(total=len(all_files), unit="file", desc="Processing") as pbar:
            for future in as_completed(futures):
                path = futures[future]
                result = future.result()

                if result in ["indexed", "skipped"]:
                    seen_paths_on_disk.add(os.path.abspath(path))

                if result in stats:
                    stats[result] += 1

                pbar.update(1)

    print("bff: Pruning deleted files from index...")
    pruned_count = 0
    hashes_to_delete = []

    for file_hash, entry in index.items():
        current_paths = entry.get("paths", [])
        new_paths = [p for p in current_paths if p in seen_paths_on_disk]

        pruned_this_hash = len(current_paths) - len(new_paths)
        pruned_count += pruned_this_hash

        if not new_paths:
            hashes_to_delete.append(file_hash)
        else:
            index[file_hash]["paths"] = new_paths

    for h in hashes_to_delete:
        del index[h]

    save_index(index, index_file_path)

    print("-" * 40)
    print("bff: Operation complete.")
    print(f" - Cached    : {stats['skipped']} (Unchanged)")
    print(f" - Indexed   : {stats['indexed']} (New/Modified)")
    print(f" - Pruned    : {pruned_count} (Deleted)")
