# tests/conftest.py
import os

import pytest


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    """
    Creates a temporary workspace and moves the process into it.
    This ensures all 'os.walk(".")' calls run in a safe sandbox.
    """
    # 1. Move to the temp directory
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def populated_workspace(workspace):
    """
    Creates a workspace with some dummy files:
    - file1.txt (content: A)
    - file2.txt (content: A) -> Duplicate
    - unique.txt (content: B)
    - .git/config (should be ignored)
    """
    # Create valid files
    with open("file1.txt", "w") as f:
        f.write("CONTENT_A")

    with open("file2.txt", "w") as f:
        f.write("CONTENT_A")  # Duplicate

    with open("unique.txt", "w") as f:
        f.write("CONTENT_B")

    # Create ignored directory
    os.makedirs(".git")
    with open(".git/config", "w") as f:
        f.write("git config")

    return workspace
