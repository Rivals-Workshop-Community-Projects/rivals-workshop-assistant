from pathlib import Path

import rivals_workshop_assistant.info_files as info_files
from rivals_workshop_assistant.paths import ASSISTANT_FOLDER

FILENAME = ".assistant"
PATH = ASSISTANT_FOLDER / FILENAME

VERSION = "version"
LAST_UPDATED = "last_updated"
PROCESSED_TIME = "processed_time"
SEEN_FILES = "seen_files"


def read_dotfile(root_dir: Path) -> dict:
    """Controller"""
    return info_files.read(root_dir / PATH)


def save_dotfile(root_dir: Path, content: dict):
    """Controller"""
    info_files.save(path=root_dir / PATH, content=content)
