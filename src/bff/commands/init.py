import json
import os

from bff.core.constants import BFF_DIR, CONFIG_FILE, INDEX_FILE


def create_bff_directory() -> bool:
    """Creates the hidden directory. Returns False if it already exists."""
    if os.path.exists(BFF_DIR):
        return False
    os.makedirs(BFF_DIR)
    return True


def create_empty_index() -> None:
    """Initializes the JSON index file with an empty dictionary."""
    with open(INDEX_FILE, "w") as f:
        json.dump({}, f, indent=4)


def create_empty_config() -> None:
    """Initializes the JSON config file with an empty dictionary."""
    with open(CONFIG_FILE, "w") as f:
        json.dump({}, f, indent=4)


def init_command() -> None:
    """Implementation of the 'init' command."""
    print("bff: Initializing project...")

    if not create_bff_directory():
        print(f"bff: Repository already exists in {BFF_DIR}.")
        return

    create_empty_index()
    create_empty_config()
    print(f"bff: Initialization complete. Created {BFF_DIR}/ structure.")
