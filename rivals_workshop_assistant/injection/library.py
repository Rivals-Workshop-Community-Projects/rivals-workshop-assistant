import re
from pathlib import Path

from . import dependency_handling

INJECT_FOLDER = 'library/inject'


def read_injection_library(
        root_path: Path) -> dependency_handling.InjectionLibrary:
    # todo if not exist, populate from a cdn I'll have to make.
    inject_gml_paths = (root_path / INJECT_FOLDER).rglob('*.gml')
    inject_gmls = [gml_path.read_text() for gml_path in inject_gml_paths]
    full_inject_gml = '\n\n'.join(inject_gmls)
    return get_injection_library_from_gml(full_inject_gml)


def get_injection_library_from_gml(
        gml: str) -> dependency_handling.InjectionLibrary:
    dependencies = []
    dependency_strings = gml.split('#')[1:]
    for dependency_string in dependency_strings:
        inject_type, name, content = _get_name_and_content(dependency_string)

        for possible_inject_type in dependency_handling.INJECT_TYPES:
            if inject_type == possible_inject_type.IDENTIFIER_STRING:
                injection = possible_inject_type.from_gml(
                    name, content
                )
                break
        else:
            raise ValueError(f'unknown inject type {inject_type}')
        dependencies.append(injection)

    return dependencies


def _get_name_and_content(gml: str) -> tuple[str, str, str]:
    inject_type, after_hash_define = gml.split(' ', maxsplit=1)
    split = re.split(pattern=r'(\s|{)', string=after_hash_define, maxsplit=1)
    return inject_type, split[0], split[1] + split[2]
