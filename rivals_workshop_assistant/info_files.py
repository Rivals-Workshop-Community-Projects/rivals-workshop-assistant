"""This file powers reading yaml files. Backend stuff."""

from ruamel.yaml import StringIO, YAML
from pathlib import Path
from rivals_workshop_assistant.file_handling import create_file

YAML_HANDLER = YAML()


def read(path: Path) -> dict:
    """Controller"""
    try:
        content = path.read_text()
    except FileNotFoundError:
        content = ""

    return _yaml_load(content)


def save(path: Path, content: dict):
    content = _yaml_dumps(content)
    create_file(path=path, content=content, overwrite=True)


def _yaml_load(yaml_str: str) -> dict:
    yaml_obj = YAML_HANDLER.load(yaml_str)
    if yaml_obj is None:
        yaml_obj = {}
    return yaml_obj


def _yaml_dumps(obj) -> str:
    with StringIO() as string_stream:
        YAML_HANDLER.dump(obj, string_stream)
        output_str = string_stream.getvalue()
    return output_str
