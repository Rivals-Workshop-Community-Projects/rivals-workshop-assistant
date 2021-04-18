from pathlib import Path

from ruamel.yaml import StringIO, YAML

from rivals_workshop_assistant import paths as paths
from rivals_workshop_assistant.file_handling import create_file

YAML_HANDLER = YAML()


VERSION = "version"
LAST_UPDATED = "last_updated"
PROCESSED_TIME = "processed_time"
SEEN_FILES = "seen_files"


def read_dotfile(root_dir: Path) -> dict:
    """Controller"""
    dotfile_path = root_dir / paths.DOTFILE_PATH
    try:
        dotfile_str = dotfile_path.read_text()
    except FileNotFoundError:
        dotfile_str = ""

    return yaml_load(dotfile_str)


def save_dotfile(root_dir: Path, dotfile: str):
    """Controller"""
    dotfile_path = root_dir / paths.DOTFILE_PATH
    create_file(path=dotfile_path, content=dotfile, overwrite=True)


def yaml_load(yaml_str: str) -> dict:
    yaml_obj = YAML_HANDLER.load(yaml_str)
    if yaml_obj is None:
        yaml_obj = {}
    return yaml_obj


def yaml_dumps(obj) -> str:
    with StringIO() as string_stream:
        YAML_HANDLER.dump(obj, string_stream)
        output_str = string_stream.getvalue()
    return output_str
