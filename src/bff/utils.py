import os


def touch(path: str) -> None:
    with open(path, "a"):
        os.utime(path, None)
