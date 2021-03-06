import re
import textwrap
from pathlib import Path

from . import dependency_handling

INJECT_FOLDER = 'inject'


def read_injection_library(root_path: Path) -> dependency_handling.InjectionLibrary:
    # todo if not exist, populate from a cdn I'll have to make.
    inject_gml_paths = (root_path / INJECT_FOLDER).rglob('*.gml')
    inject_gmls = [gml_path.read_text() for gml_path in inject_gml_paths]
    full_inject_gml = '\n\n'.join(inject_gmls)
    return get_injection_library_from_gml(full_inject_gml)


def get_injection_library_from_gml(gml: str) -> dependency_handling.InjectionLibrary:
    dependencies = []
    dependency_strings = gml.split('#')[1:]
    for dependency_string in dependency_strings:
        name, content = _get_name_and_content(dependency_string)

        content = _remove_brackets(content)

        content = textwrap.dedent(content).strip('\n')

        docs, content = _split_docs_and_gml(content)

        dependencies.append(dependency_handling.Define(name=name, docs=docs, content=content))
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
    after_hash_define = gml.split('define ')[1]  # todo, this assumes its define, support macro
    split = re.split(pattern=r'(\s|{)', string=after_hash_define, maxsplit=1)
    return split[0], split[1] + split[2]


"""

'    several
    different   
        indentations
    to
handle'




name_params_version, content = gml.split('\n', 1)
    name, params, version = _extract_name_params_version(name_params_version)

    docs, gml = _extract_docs_gml(content)

    for dependency_type in (DEPENDENCY_TYPES):
        if gml.startswith(dependency_type.IDENTIFIER_STRING):
            return dependency_type(
                name=name,
                params=params,
                version=version,
                docs=docs,
                gml=gml,
                depends=used_dependencies)
    raise ValueError("Given gml doesn't look like a support dependency.")


def _extract_name_params_version(name_params_version_line: str) -> t.Tuple[str, t.List[str], int]:
    name_params_version = name_params_version_line.replace(Define.IDENTIFIER_STRING, '').strip()
    has_version = '//' in name_params_version
    if has_version:
        name_params, version_str = [section.strip() for section in name_params_version.split('//')]
        version = int(re.findall(r'\d+', version_str)[0])
    else:
        name_params = name_params_version
        version = 0

    has_params = '(' in name_params
    if has_params:
        name, params_str = name_params.split('(')
        params = params_str.replace(')', '').replace(' ', '').split(',')
    else:
        name = name_params
        params = []
    return name, params, version


def _is_documentation_line(line: str) -> bool:
    return line.replace(' ', '').replace('\t', '').startswith('//')


def _remove_documentation_prefix_from_line(line: str) -> str:
    return re.sub(r'//\s*', '', line)


def _extract_docs_gml(docs_gml: str) -> t.Tuple[str, str]:
    content_lines = docs_gml.split('\n')
    doc_lines = []
    gml_lines = []
    for line in content_lines:
        if not gml_lines and _is_documentation_line(line):
            line = _remove_documentation_prefix_from_line(line)
            doc_lines.append(line)
        else:
            gml_lines.append(line)

    docs = '\n'.join(doc_lines)
    gml = '\n'.join(gml_lines)
    return docs, gml"""
