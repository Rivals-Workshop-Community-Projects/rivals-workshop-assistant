import functools
from pathlib import Path
from datetime import datetime

from rivals_workshop_assistant import aseprite_loading


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
        original_content: str,
        working_content: str = None,
        processed_time: datetime = None,
    ):
        super().__init__(path, modified_time, processed_time)
        self.original_content = original_content

        if working_content is None:
            working_content = original_content
        self.working_content = working_content

    def save(self, root_dir: Path):
        with open((root_dir / self.path), "w", newline="\n") as f:
            f.write(self.working_content)

    def __eq__(self, other: "Script"):
        return (
            self.path == other.path
            and self.original_content == other.original_content
            and self.working_content == other.working_content
            and self.is_fresh == other.is_fresh
        )


class Anim(File):
    def __init__(
        self,
        path: Path,
        modified_time: datetime,
        processed_time: datetime = None,
    ):
        super().__init__(path, modified_time, processed_time)

    @functools.cached_property
    def content(self):
        with open(self.path, "rb") as f:
            contents = f.read()
        return aseprite_loading.AsepriteFile(contents)

    def save(self, root_dir: Path):
        # Will need aseprite path, and small_sprites setting
        raise NotImplementedError
