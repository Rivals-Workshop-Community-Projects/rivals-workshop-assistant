from datetime import datetime
from pathlib import Path


def create_file(path: Path, content: str, overwrite=False):
    """Creates or overwrites the file with the given content"""
    path.parent.mkdir(exist_ok=True)
    if not overwrite and path.exists():
        return

    with open(path, "w+", newline="\n") as f:
        f.write(content)


def _get_is_fresh(processed_time: datetime, modified_time: datetime):
    if processed_time is None:
        return True
    return processed_time < modified_time


class File:
    def __init__(
        self,
        path: Path,
        modified_time: datetime = None,
        processed_time: datetime = None,
    ):
        if modified_time is None:
            modified_time = _get_modified_time(path)

        self.path = path
        self.is_fresh = _get_is_fresh(processed_time, modified_time)


def _get_modified_time(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime)
