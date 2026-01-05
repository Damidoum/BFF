import os
import sys
from typing import Set

from bff.core.constants import BFF_DIR, INDEX_FILE
from bff.core.index_manager import load_index


def _resolve_index_path(target_path: str) -> str:
    """
    Resolves the path to the index file.
    Accepts either a root repository directory or a direct path to index.json.
    """
    if os.path.isdir(target_path):
        # 1. Standard repository structure
        repo_index = os.path.join(target_path, BFF_DIR, "index.json")
        if os.path.exists(repo_index):
            return repo_index

        # 2. Direct folder pointer (e.g., pointing to .bff/ directly)
        direct_index = os.path.join(target_path, "index.json")
        if os.path.basename(target_path) == BFF_DIR and os.path.exists(direct_index):
            return direct_index

        print(f"Error: The directory '{target_path}' is not a valid BFF repository.")
        sys.exit(1)

    elif os.path.isfile(target_path):
        return target_path

    else:
        print(f"Error: Path '{target_path}' does not exist.")
        sys.exit(1)


def diff_command(target: str) -> None:
    # 1. Resolve Remote Path
    remote_index_path = _resolve_index_path(target)

    # 2. Load Local Index
    if not os.path.exists(INDEX_FILE):
        print("Error: Local repository not initialized. Run 'init' first.")
        return

    print("bff: Loading local index...")
    local_index = load_index()
    local_hashes: Set[str] = set(local_index.keys())

    # 3. Load Remote Index
    print(f"bff: Loading remote index from '{remote_index_path}'...")
    # Use standard load_index since logic is generic now
    remote_index = load_index(remote_index_path)
    remote_hashes: Set[str] = set(remote_index.keys())

    # 4. Compute Set Differences
    common = local_hashes & remote_hashes
    only_local = local_hashes - remote_hashes
    only_remote = remote_hashes - local_hashes

    # 5. Generate Report
    print("\n" + "=" * 60)
    print("BFF DIFFERENTIAL REPORT")
    print(f"Local Path:  {os.getcwd()}")
    print(f"Target Path: {os.path.dirname(os.path.dirname(remote_index_path))}")
    print("=" * 60)

    print(f"Total Local Files  : {len(local_hashes)}")
    print(f"Total Target Files : {len(remote_hashes)}")
    print("-" * 60)

    # [OVERLAP]
    if common:
        size_common = sum(local_index[h]["size"] for h in common)
        print(f"[=] OVERLAP (Identical Content) : {len(common)} files")
        print(f"    Shared Data Volume          : {size_common / (1024 * 1024):.2f} MB")
    else:
        print("[=] OVERLAP                     : 0 files")

    # [LOCAL ONLY]
    print(f"[-] LOCAL ONLY (Unique here)    : {len(only_local)} files")

    # [REMOTE ONLY]
    print(f"[+] TARGET ONLY (Unique there)  : {len(only_remote)} files")

    print("=" * 60)

    # Preview of missing files
    if only_remote:
        print("\n[Preview] Content found in Target but MISSING locally:")
        count = 0
        for h in list(only_remote):
            if count >= 5:
                break

            # Retrieve metadata from the remote index
            remote_entry = remote_index[h]
            path = remote_entry["paths"][0]
            size_mb = remote_entry["size"] / (1024 * 1024)

            filename = os.path.basename(path)
            print(f" - {filename:<30} ({size_mb:.2f} MB)")
            count += 1

        if len(only_remote) > 5:
            print(f"   ... and {len(only_remote) - 5} more.")
