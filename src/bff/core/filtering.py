import os
from typing import List, Optional


class IndexFilters:
    """Configuration object for file filtering criteria."""

    def __init__(
        self,
        extensions: Optional[List[str]] = None,
        min_size_bytes: int = 0,
        after_date: Optional[float] = None,
    ):
        self.extensions = [e.lower() for e in extensions] if extensions else None
        self.min_size_bytes = min_size_bytes
        self.after_date = after_date


def should_index(filepath: str, filters: IndexFilters) -> bool:
    """
    Determines if a file matches the filtering criteria.
    Public function used by both index and clean commands.
    """
    # 1. Symlink check
    if os.path.islink(filepath):
        return False

    # 2. Extension check
    if filters.extensions:
        _, ext = os.path.splitext(filepath)
        if ext.lower() not in filters.extensions:
            return False

    try:
        stat = os.stat(filepath)

        # 3. Size check
        if stat.st_size < filters.min_size_bytes:
            return False

        # 4. Date check
        if filters.after_date and stat.st_ctime < filters.after_date:
            return False

        return True

    except OSError:
        # File might be locked or deleted during check
        return False
