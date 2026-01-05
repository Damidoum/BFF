import shutil
import sys

from bff.core.constants import BFF_DIR
from bff.core.index_manager import find_repository_root


def reset_command(force: bool = False) -> None:
    """
    Deletes the .bff directory completely.
    """
    root = find_repository_root()
    if not root:
        print("bff: No repository found. Nothing to reset.")
        return

    # Security Warning
    if not force:
        print(
            "WARNING: This will delete the internal database, index, and history log."
        )
        print(
            "This will NOT undo changes already made to your files (symlinks/deletions)."
        )
        print("You will lose the ability to track previous operations.")

        response = (
            input(f"Are you sure you want to delete {BFF_DIR}/? [y/N]: ")
            .strip()
            .lower()
        )
        if response != "y":
            print("bff: Reset aborted.")
            return

    try:
        shutil.rmtree(f"{root}/{BFF_DIR}")
        print(f"bff: Repository reset. {BFF_DIR}/ has been removed.")
    except OSError as e:
        print(f"Error: Could not remove directory ({e}). Check permissions.")
        sys.exit(1)
