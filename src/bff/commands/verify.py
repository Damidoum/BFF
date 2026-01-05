import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Tuple

from tqdm import tqdm

from bff.core.hash import hash_file
from bff.core.index_manager import load_index


def _verify_file(stored_hash: str, filepath: str) -> Tuple[str, str, str]:
    """
    Worker function to verify a single file.
    Returns tuple: (status, filepath, message)
    Status codes: 'OK', 'CORRUPT', 'MISSING', 'ERROR'
    """
    if not os.path.exists(filepath):
        return "MISSING", filepath, "File not found"

    try:
        current_hash = hash_file(filepath)
        if current_hash != stored_hash:
            return (
                "CORRUPT",
                filepath,
                f"Hash mismatch. Expected {stored_hash[:8]}, got {current_hash[:8]}",
            )
        return "OK", filepath, ""
    except Exception as e:
        return "ERROR", filepath, str(e)


def verify_command() -> None:
    print("bff: Loading index for integrity check...")
    index = load_index()

    if not index:
        print("bff: Index is empty or missing.")
        return

    # Prepare tasks
    tasks = []
    for stored_hash, entry in index.items():
        for path in entry.get("paths", []):
            tasks.append((stored_hash, path))

    total_files = len(tasks)
    print(f"bff: Verifying {total_files} files against stored signatures...")

    corrupted_files = []
    missing_files = []
    errors = []

    # Use CPU count + 4 for I/O bound tasks
    max_workers = min(32, (os.cpu_count() or 1) + 4)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_verify_file, h, p): p for h, p in tasks}

        with tqdm(total=total_files, unit="file", desc="Verifying") as pbar:
            for future in as_completed(futures):
                status, filepath, msg = future.result()

                if status == "CORRUPT":
                    corrupted_files.append((filepath, msg))
                elif status == "MISSING":
                    missing_files.append(filepath)
                elif status == "ERROR":
                    errors.append((filepath, msg))

                pbar.update(1)

    print("\n" + "-" * 40)
    print("INTEGRITY CHECK REPORT")
    print("-" * 40)

    if not corrupted_files and not missing_files and not errors:
        print("Result: PASSED. All files are healthy.")
    else:
        print("Result: FAILED. Issues detected.")

        if corrupted_files:
            print(f"\n[!] CORRUPTED FILES ({len(corrupted_files)}):")
            for path, msg in corrupted_files:
                print(f"  - {path} ({msg})")

        if missing_files:
            print(f"\n[!] MISSING FILES ({len(missing_files)}):")
            for path in missing_files:
                print(f"  - {path}")

        if errors:
            print(f"\n[!] READ ERRORS ({len(errors)}):")
            for path, msg in errors:
                print(f"  - {path}: {msg}")
