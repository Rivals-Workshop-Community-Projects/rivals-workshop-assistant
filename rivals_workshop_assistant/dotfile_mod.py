import datetime
import typing
from datetime import datetime
from pathlib import Path

import rivals_workshop_assistant.info_files as info_files
from rivals_workshop_assistant.file_handling import File
from rivals_workshop_assistant.paths import ASSISTANT_FOLDER

FILENAME = ".assistant"
PATH = ASSISTANT_FOLDER / FILENAME

LIBRARY_VERSION_FIELD = "library_version"


def get_library_version_string(dotfile: dict) -> typing.Optional[str]:
    return dotfile.get(LIBRARY_VERSION_FIELD, None)


ASSISTANT_VERSION_FIELD = "assistant_version"


def get_assistant_version_string(dotfile: dict) -> typing.Optional[str]:
    return dotfile.get(ASSISTANT_VERSION_FIELD, None)


LAST_UPDATED_FIELD = "last_updated"
PROCESSED_TIME_FIELD = "processed_time"
SEEN_FILES_FIELD = "seen_files"


def read(root_dir: Path) -> dict:
    """Controller"""
    return info_files.read(root_dir / PATH)


def save_dotfile(root_dir: Path, content: dict):
    """Controller"""
    info_files.save(path=root_dir / PATH, content=content)


def update_dotfile_after_saving(
    dotfile: dict, now: datetime, seen_files: typing.List[File]
):
    dotfile[PROCESSED_TIME_FIELD] = now
    dotfile[SEEN_FILES_FIELD] = [file.path.as_posix() for file in seen_files]


def get_processed_time(dotfile: dict, path: Path) -> typing.Optional[datetime]:
    seen_files = dotfile.get(SEEN_FILES_FIELD, [])
    if seen_files is None:
        seen_files = []
    if path.as_posix() in seen_files:
        return dotfile.get(PROCESSED_TIME_FIELD, None)
    else:
        return None
