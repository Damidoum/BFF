import hashlib


def hash_file(filepath: str, chunk_size: int = 65536) -> str:
    """
    Computes SHA-256 hash by reading the file in chunks.
    Safe for large files (e.g., 50GB videos) as it uses constant RAM.
    """
    sha256 = hashlib.sha256()

    with open(filepath, "rb") as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            sha256.update(data)

    return sha256.hexdigest()
