from pathlib import Path

from ruamel.yaml import StringIO, YAML

from rivals_workshop_assistant import paths as paths
from rivals_workshop_assistant.file_handling import create_file


def read_dotfile(root_dir: Path):
    """Controller"""
    dotfile_path = root_dir / paths.DOTFILE_PATH
    try:
        return dotfile_path.read_text()
    except FileNotFoundError:
        return ""


def save_dotfile(root_dir: Path, dotfile: str):
    """Controller"""
    dotfile_path = root_dir / paths.DOTFILE_PATH
    create_file(path=dotfile_path, content=dotfile, overwrite=True)


def yaml_load(yaml_str: str):
    yaml_obj = yaml_handler.load(yaml_str)
    if yaml_obj is None:
        yaml_obj = {}
    return yaml_obj


def yaml_dumps(obj) -> str:
    with StringIO() as string_stream:
        yaml_handler.dump(obj, string_stream)
        output_str = string_stream.getvalue()
    return output_str


yaml_handler = YAML()
