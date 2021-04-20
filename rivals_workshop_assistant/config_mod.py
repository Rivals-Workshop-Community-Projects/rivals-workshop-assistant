from pathlib import Path

import rivals_workshop_assistant.info_files as info_files
from rivals_workshop_assistant.paths import ASSISTANT_FOLDER

FILENAME = "assistant_config.ini"
PATH = ASSISTANT_FOLDER / FILENAME


def read_config(root_dir: Path) -> dict:
    """Controller"""
    return info_files.read(root_dir / PATH)
