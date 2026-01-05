import os

from bff.core.constants import BFF_DIR
from bff.core.index_manager import load_index


def _format_size(size_bytes: int) -> str:
    """Helper to make sizes readable (KB, MB, GB)."""
    size_bytes_f = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes_f < 1024.0:
            return f"{size_bytes_f:.2f} {unit}"
        size_bytes_f /= 1024.0
    return f"{size_bytes_f:.2f} TB"


def stats_command() -> None:
    if not os.path.exists(BFF_DIR):
        print("Error: No bff repository found.")
        return

    index = load_index()

    total_files = 0
    unique_files = len(index)
    total_size = 0
    wasted_size = 0
    duplicate_count = 0

    for _, data in index.items():
        paths = data.get("paths", [])
        count = len(paths)
        size = data.get("size", 0)

        total_files += count
        total_size += count * size

        if count > 1:
            # Wasted space = size * (number of copies - 1 master)
            wasted_size += size * (count - 1)
            duplicate_count += count - 1

    print("-" * 30)
    print("BFF REPOSITORY STATISTICS")
    print("-" * 30)
    print(f"Unique Content : {unique_files}")
    print(f"Total Files    : {total_files}")
    print(f"Total Size     : {_format_size(total_size)}")
    print("-" * 30)
    print(f"Duplicates     : {duplicate_count}")
    print(f"Reclaimable    : {_format_size(wasted_size)}")
    print("-" * 30)
