import textwrap
import typing

import parse

from rivals_workshop_assistant.paths import Scripts


def handle_codegen(scripts: Scripts) -> Scripts:
    scripts = scripts.copy()
    for path, script in scripts.items():
        scripts[path] = handle_codegen_for_script(script)
    return scripts


def handle_codegen_for_script(script: str) -> str:
    lines = script.split('\n')
    new_lines = [handle_codegen_for_line(line)
                 for line in lines]
    script = '\n'.join(new_lines)
    return script


def handle_codegen_for_line(line: str) -> str:
    if get_line_before_comment(line).count('$') == 2:
        before, seed, after = line.split('$')
    else:
        return line

    code = handle_codegen_for_seed(seed)
    if code:
        if before.isspace():
            indented_code = textwrap.indent(text=code, prefix=before)
            return f'{indented_code}{after}'
        else:
            return f'{before}{code}{after}'
    else:
        return f'{line} // ERROR: No code injection match found'


def handle_codegen_for_seed(seed: str) -> str:
    new_line = handle_foreach_codegen(seed)

    return new_line


def handle_foreach_codegen(seed) -> typing.Optional[str]:
    try:
        collection_name = parse.parse(
            'foreach {collection}', seed)['collection']
    except TypeError:
        return None

    item_name = collection_name + '_item'
    iterator_name = item_name + '_i'

    code = f'''\
for (var {iterator_name} = 0; {iterator_name}++; {iterator_name} < array_length({collection_name}) {{
    var {item_name} = {collection_name}[{iterator_name}]
}}'''
    return code


def get_line_before_comment(line: str) -> str:
    return line.split(r'//')[0]
