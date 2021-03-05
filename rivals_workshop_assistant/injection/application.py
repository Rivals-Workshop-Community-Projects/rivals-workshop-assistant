import re
import typing as t
from pathlib import Path

from .dependency_handling import InjectionLibrary, GmlInjection

INJECTION_START_MARKER = '// vvv LIBRARY DEFINES AND MACROS vvv\n'
INJECTION_START_WARNING = ('// DANGER File below this point will be overwritten! Generated defines and macros below.'
                           '// Write NO-INJECT in a comment above this area to disable injection.')
INJECTION_START_HEADER = (
    f'{INJECTION_START_MARKER}'
    f'{INJECTION_START_WARNING}')
INJECTION_END_HEADER = (
    '// DANGER: Write your code ABOVE the LIBRARY DEFINES AND MACROS header or it will be overwritten!')


def apply_injection(scripts: t.Dict[Path, str], injection_library: InjectionLibrary) -> t.Dict[Path, str]:
    """Creates a new scripts collection where each script has updated supplied dependencies."""
    result_scripts = scripts.copy()
    for path, script in scripts.items():
        result_scripts[path] = _apply_injection_to_script(script, injection_library)

    return result_scripts


def _apply_injection_to_script(script: str, injection_library: InjectionLibrary) -> str:
    """Updates the dependencies supplied to the script."""
    if _should_inject(script):
        dependency_gmls = _get_injection_gmls_used_in_script(script, injection_library)
        return _add_inject_gmls_in_script(script, dependency_gmls)
    else:
        return script


def _should_inject(script):
    return 'NO-INJECT' not in _get_script_contents(script)


def _get_injection_gmls_used_in_script(script: str, injection_library: InjectionLibrary) -> t.List[str]:
    """Gets the gml content of each injection used by the script."""
    return [injection.gml
            for injection in _get_injections_used_in_gml(gml=script, injection_library=injection_library)
            ]


def _get_injections_used_in_gml(
        gml: str,
        injection_library: InjectionLibrary,
        existing_injections: InjectionLibrary = None) -> InjectionLibrary:
    if existing_injections is None:
        injections = []
    else:
        injections = existing_injections

    for injection in injection_library:
        if (injection not in injections
                and _injection_is_used_in_script(script=gml, injection=injection)):
            injections.append(injection)
            recursive_injections = _get_injections_used_in_gml(
                gml=injection.gml,
                injection_library=injection_library,
                existing_injections=injections
            )
            injections += [recursive_injection for recursive_injection in recursive_injections
                           if recursive_injection not in injections]
    return injections


def _injection_is_used_in_script(script, injection: GmlInjection):
    return re.search(pattern=injection.use_pattern, string=script)


def _add_inject_gmls_in_script(script: str, dependency_gmls: t.List[str]) -> str:
    """Returns the script after supplying dependencies."""
    script_content = _get_script_contents(script)
    new_script = script_content
    if dependency_gmls:
        injection_gml = '\n\n'.join(dependency_gmls)
        new_script += f"""\


{INJECTION_START_HEADER}
{injection_gml}
{INJECTION_END_HEADER}"""
    return new_script


def _get_script_contents(script: str):
    """Get the portion of the script above the dependency header."""
    return script.split(INJECTION_START_MARKER)[0].strip()
