import typing
from pathlib import Path

import rivals_workshop_assistant.info_files as info_files
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
