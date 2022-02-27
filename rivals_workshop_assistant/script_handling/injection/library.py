import itertools
import re
from pathlib import Path
from typing import List, Tuple

import rivals_workshop_assistant.paths
from .dependency_handling import (
    GmlInjection,
    INJECT_TYPES,
    _strip_non_content_lines,
    _normalize_block_comments,
)


def read_injection_library(root_dir: Path) -> List[GmlInjection]:
    """Controller"""
    inject_gml_paths = list(
        (root_dir / rivals_workshop_assistant.paths.INJECT_FOLDER).rglob("*.gml")
    ) + list(
        (root_dir / rivals_workshop_assistant.paths.USER_INJECT_FOLDER).rglob("*.gml")
    )

    full_lib = []
    for file in inject_gml_paths:
        full_lib.extend(get_injection_library_from_file(file))
    return full_lib


def grouper(n, iterable, fillvalue=None):
    """grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"""
    args = [iter(iterable)] * n
    return itertools.zip_longest(fillvalue=fillvalue, *args)


def get_dependency_strings(dependency_splits: List[str]):
    if not dependency_splits[0].startswith("#"):
        dependency_splits = dependency_splits[1:]
    dependency_strings = [
        f"{dependency_type}{content}"
        for dependency_type, content in grouper(2, dependency_splits)
    ]
    return dependency_strings


def get_injection_library_from_gml(gml: str) -> List[GmlInjection]:
    dependencies = []
    dependency_splits = re.split(
        "(#(?:define|macro))", gml
    )  # literally having define|macro is duplication with INJECT_TYPES, but simpler
    dependency_strings = get_dependency_strings(dependency_splits)
    for dependency_string in dependency_strings:
        inject_type, name, content = _get_inject_components(dependency_string)

        for possible_inject_type in INJECT_TYPES:
            if inject_type == possible_inject_type.IDENTIFIER_STRING:
                injection = possible_inject_type.from_gml(name, content)
                break
        else:
            raise ValueError(f"unknown inject type {inject_type}")
        dependencies.append(injection)

    return dependencies


def get_injection_library_from_file(gml_path: Path) -> List[GmlInjection]:
    dependencies = get_injection_library_from_gml(gml_path.read_text())
    #saving filepath ideally done through constructor 
    #didn't feel like upsetting signature of all other functions just yet
    for dep in dependencies:
        dep.filepath = gml_path
    return dependencies


def _get_inject_components(gml: str) -> Tuple[str, str, str]:
    inject_type, after_inject_type = gml.split(" ", maxsplit=1)
    inject_type = inject_type.split("#")[1]
    if "(" in after_inject_type:
        pattern = r"(\n|{)"
    else:
        pattern = r"(\s|{)"
    split = re.split(pattern=pattern, string=after_inject_type, maxsplit=1)

    name = split[0]
    content = split[1] + split[2]
    content = _normalize_block_comments(content)
    content = _strip_non_content_lines(content)

    return inject_type, name, content
