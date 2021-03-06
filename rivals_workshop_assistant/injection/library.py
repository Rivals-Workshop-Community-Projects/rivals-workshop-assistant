import re
import textwrap
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
        name, content = _get_name_and_content(dependency_string)

        content = _remove_brackets(content)

        content = textwrap.dedent(content).strip('\n')

        docs, content = _split_docs_and_gml(content)

        dependencies.append(
            dependency_handling.Define(name=name, docs=docs, content=content))
    return dependencies


def _remove_brackets(content):
    has_start_bracket = content.strip().startswith('{')
    has_end_bracket = content.strip().endswith('}')
    if has_start_bracket != has_end_bracket:
        raise ValueError("Mismatched curly braces")
    if has_start_bracket and has_end_bracket:
        content = content.strip().lstrip('{').rstrip('}').strip('\n')
    return content


def _split_docs_and_gml(content: str) -> tuple[str, str]:
    lines = content.split('\n')
    non_docs_found = False

    doc_lines = []
    gml_lines = []
    for line in lines:
        if not non_docs_found:
            if line.lstrip().startswith('//'):
                line = line.split('//')[1].rstrip()
                if line[0] == ' ':  # Remove padding from '// ' format
                    line = line[1:]
                doc_lines.append(line)
                continue
            else:
                non_docs_found = True
        gml_lines.append(line.rstrip())

    return '\n'.join(doc_lines), '\n'.join(gml_lines)


def _get_name_and_content(gml: str) -> tuple[str, str]:
    after_hash_define = gml.split('define ')[
        1]  # todo, this assumes its define, support macro
    split = re.split(pattern=r'(\s|{)', string=after_hash_define, maxsplit=1)
    return split[0], split[1] + split[2]
