# tests/test_hash.py
import hashlib

from bff.core.hash import hash_file


def test_hash_file_correctness(tmp_path):
    # Setup
    p = tmp_path / "test.txt"
    content = b"Hello World"
    p.write_bytes(content)

    # Expected SHA256 for "Hello World"
    expected = hashlib.sha256(content).hexdigest()

    # Assert
    assert hash_file(str(p)) == expected


def test_hash_empty_file(tmp_path):
    p = tmp_path / "empty.txt"
    p.write_bytes(b"")

    # SHA256 of empty string
    expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert hash_file(str(p)) == expected
