# tests/test_cli.py
import json
import os

from bff.commands.check import check_command
from bff.commands.clean import clean_command
from bff.commands.index import IndexFilters, index_command
from bff.commands.init import init_command


def load_db():
    """Helper to read the generated json DB"""
    with open(".bff/index.json", "r") as f:
        return json.load(f)


def test_init_command(workspace):
    init_command()
    assert os.path.exists(".bff")
    assert os.path.exists(".bff/index.json")


def test_init_command_idempotency(workspace):
    """Running init twice shouldn't crash"""
    init_command()
    init_command()  # Should print "already exists" and pass
    assert os.path.isdir(".bff")


def test_index_deduplication(populated_workspace):
    """Should find 2 files but identify them as 1 unique content"""
    init_command()

    # Run index with default filters
    index_command(IndexFilters())

    data = load_db()

    # We expect 2 unique hashes (CONTENT_A and CONTENT_B)
    # The .git file should be ignored
    assert len(data) == 2

    # Find the entry for CONTENT_A
    content_a_entry = next(
        v
        for k, v in data.items()
        if v["paths"][0].endswith("file1.txt") or v["paths"][0].endswith("file2.txt")
    )

    # Check that deduplication worked: 1 hash -> 2 paths
    assert len(content_a_entry["paths"]) == 2
    assert "file1.txt" in str(content_a_entry["paths"])
    assert "file2.txt" in str(content_a_entry["paths"])


def test_clean_delete_mode(populated_workspace):
    """Test actual deletion of duplicates"""
    init_command()
    index_command(IndexFilters())

    # Pre-check
    assert os.path.exists("file1.txt")
    assert os.path.exists("file2.txt")

    # Clean
    clean_command(use_symlinks=False)

    # Post-check: file1 should remain (master), file2 should be gone
    # (Note: exact master depends on list order, but one must survive)
    remaining = os.path.exists("file1.txt") or os.path.exists("file2.txt")
    both = os.path.exists("file1.txt") and os.path.exists("file2.txt")

    assert remaining is True
    assert both is False  # One should be gone


def test_clean_symlink_mode(populated_workspace):
    """Test replacement with symlinks"""
    init_command()
    index_command(IndexFilters())

    clean_command(use_symlinks=True)

    # Both filenames should still exist
    assert os.path.exists("file1.txt")
    assert os.path.exists("file2.txt")

    # But one of them should be a symlink
    is_link_1 = os.path.islink("file1.txt")
    is_link_2 = os.path.islink("file2.txt")

    # XOR: One is link, one is file
    assert is_link_1 != is_link_2


def test_check_prune(populated_workspace):
    """Test removing missing files from index"""
    init_command()
    index_command(IndexFilters())

    # Manually delete a file bypassing BFF
    os.remove("unique.txt")

    # Verify DB still thinks it exists
    data = load_db()
    assert len(data) == 2  # Still has CONTENT_A and CONTENT_B

    # Run check with prune
    check_command(prune=True)

    # DB should be updated
    data = load_db()
    assert len(data) == 1  # Only CONTENT_A remains
