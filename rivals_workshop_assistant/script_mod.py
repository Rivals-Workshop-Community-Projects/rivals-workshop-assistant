import functools
from pathlib import Path
from datetime import datetime


def _get_is_fresh(processed_time: datetime, modified_time: datetime):
    if processed_time is None:
        return True
    return processed_time < modified_time


class File:
    def __init__(
        self,
        path: Path,
        modified_time: datetime,
        processed_time: datetime = None,
    ):
        self.path = path
        self.is_fresh = _get_is_fresh(processed_time, modified_time)


class Script(File):
    def __init__(
        self,
        path: Path,
        modified_time: datetime,
        original_content: str = None,
        working_content: str = None,
        processed_time: datetime = None,
    ):
        super().__init__(path, modified_time, processed_time)
        self._original_content = original_content
        self._working_content = working_content

        self.working_content = working_content

    @functools.cached_property
    def original_content(self):
        if self._original_content is None:
            self._original_content = self.path.read_text(
                encoding="UTF8", errors="surrogateescape"
            )
        return self._original_content

    @property
    def working_content(self):
        if self._working_content is None:
            self._working_content = self.original_content
        return self._working_content

    @working_content.setter
    def working_content(self, value):
        self._working_content = value

    def save(self, root_dir: Path):
        with open(
            (root_dir / self.path),
            "w",
            encoding="UTF8",
            errors="surrogateescape",
            newline="\n",
        ) as f:
            f.write(self.working_content)

    def __eq__(self, other: "Script"):
        return (
            self.path == other.path
            and self.original_content == other.original_content
            and self.working_content == other.working_content
            and self.is_fresh == other.is_fresh
        )
