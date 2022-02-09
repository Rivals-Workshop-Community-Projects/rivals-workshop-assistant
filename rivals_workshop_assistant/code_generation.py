import textwrap
import typing

import parse
from inflector import English

from rivals_workshop_assistant.script_mod import Script
from typing import List


def handle_codegen(scripts: List[Script]):
    for script in scripts:
        if script.is_fresh:
            script.working_content = handle_codegen_for_script(script.working_content)


def handle_codegen_for_script(content: str) -> str:
    lines = content.split("\n")
    new_lines = [handle_codegen_for_line(line) for line in lines]
    content = "\n".join(new_lines)
    return content


def handle_codegen_for_line(line: str) -> str:
    if get_line_before_comment(line).count("$") == 2:
        before, seed, after = line.split("$")
    else:
        return line

    if "{" in seed:  # Avoids false alarms on `` format strings.
        return line

    code = handle_codegen_for_seed(seed)
    if code:
        if before.isspace():
            indented_code = textwrap.indent(text=code, prefix=before)
            return f"{indented_code}{after}"
        else:
            return f"{before}{code}{after}"
    else:
        return line
        # return f"{line} // ERROR: No code injection match found"
        # temporarily disabled because of false alarms when $ is used as a color indicator.


def handle_codegen_for_seed(seed: str) -> typing.Optional[str]:
    for handle_codegen in (handle_foreach_codegen, handle_safe_with_codegen):
        new_line = handle_codegen(seed)
        if new_line:
            return new_line
    return None


def handle_foreach_codegen(seed) -> typing.Optional[str]:
    try:
        collection_name = parse.parse("foreach {collection}", seed)["collection"]
    except TypeError:
        return None

    item_name = singularize(collection_name)
    iterator_name = item_name + "_i"

    code = f"""\
for (var {iterator_name}=0; {iterator_name}<array_length({collection_name}); {iterator_name}++) {{
    var {item_name} = {collection_name}[{iterator_name}]
}}"""
    return code


def handle_safe_with_codegen(seed) -> typing.Optional[str]:
    """
    $safewith(obj)$ --> for(var i = 0; i < instance_number(obj);i++) with instance_find(obj,i)
    """
    try:
        obj = parse.parse("safewith {obj}", seed)["obj"]
    except TypeError:
        return None

    code = f"""\
for (var obj_i=0; obj_i<instance_number({obj}); obj_i++) {{
    with instance_find(obj, obj_i) {{
    
    }}
}}"""
    return code


def get_line_before_comment(line: str) -> str:
    return line.split(r"//")[0]


_inflector_singularize = English().singularize


def singularize(string: str):
    string = string.lower()
    inflector_attempt = _inflector_singularize(string)
    if inflector_attempt == string:
        return f"{string}_item"
    else:
        return inflector_attempt
