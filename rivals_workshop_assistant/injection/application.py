import re
import typing

from .dependency_handling import GmlInjection
from rivals_workshop_assistant.script_mod import Script
from ..aseprite_handling import Anim
from typing import List

INJECTION_START_MARKER = "// vvv LIBRARY DEFINES AND MACROS vvv\n"
INJECTION_START_WARNING = (
    "// DANGER File below this point will be overwritten! "
    "Generated defines and macros below.\n"
    "// Write NO-INJECT in a comment above this area to disable injection."
)
INJECTION_START_HEADER = f"{INJECTION_START_MARKER}{INJECTION_START_WARNING}"
INJECTION_END_HEADER = (
    "// DANGER: "
    "Write your code ABOVE the LIBRARY DEFINES AND MACROS header "
    "or it will be overwritten!"
)


def apply_injection(
    scripts: List[Script], injection_library: List[GmlInjection], anims: List[Anim]
):
    """Updates scripts with supplied dependencies."""
    for script in scripts:
        anim = _get_anim_for_script(script, anims)
        if script.is_fresh or (anim is not None and anim.is_fresh):
            _apply_injection_to_script(script, injection_library, anim)


def _apply_injection_to_script(
    script: Script, injection_library: List[GmlInjection], anim: Anim
):
    """Updates the dependencies supplied to the script."""
    if _should_inject(script.working_content):
        needed_gmls = _get_inject_gmls_needed_in_gml(
            script.working_content, injection_library
        ) + _get_anim_data_gmls_needed_in_gml(anim)
        script.working_content = _add_inject_gmls_in_script(
            script.working_content, needed_gmls
        )


def _should_inject(script: str):
    return "NO-INJECT" not in _get_script_contents(script)  # Performance problem?


def _get_anim_data_gmls_needed_in_gml(anim: Anim):
    if anim is None:
        return []
    window_gmls = [window.gml for window in anim.windows]
    return window_gmls


def _get_anim_for_script(script: Script, anims: List[Anim]) -> typing.Optional[Anim]:
    if script.path.parent.name != "attacks":
        return None
    anim = next((anim for anim in anims if anim.name == script.path.stem), None)
    return anim


def _get_inject_gmls_needed_in_gml(
    gml: str, injection_library: List[GmlInjection]
) -> List[str]:
    needed_injects = _get_injects_needed_in_gml(gml, injection_library)
    return [injection.gml for injection in needed_injects]


def _get_injects_needed_in_gml(gml: str, injection_library: List[GmlInjection]):
    used_injects = _get_injects_used_in_gml(gml, injection_library)
    needed_injects = [
        inject for inject in used_injects if not _gml_supplies_inject(gml, inject)
    ]
    return needed_injects


def _get_injects_used_in_gml(
    gml: str,
    injection_library: List[GmlInjection],
    existing_injections: List[GmlInjection] = None,
) -> List[GmlInjection]:
    if existing_injections is None:
        injections = []
    else:
        injections = existing_injections

    for injection in injection_library:
        if injection not in injections and _gml_uses_inject(
            gml=gml, injection=injection
        ):
            injections.append(injection)
            recursive_injections = _get_injects_used_in_gml(
                gml=injection.gml,
                injection_library=injection_library,
                existing_injections=injections,
            )
            injections += [
                recursive_injection
                for recursive_injection in recursive_injections
                if recursive_injection not in injections
            ]
    return injections


def _gml_uses_inject(gml: str, injection: GmlInjection):
    return re.search(pattern=injection.use_pattern, string=gml)


def _gml_supplies_inject(gml: str, inject: GmlInjection):
    return re.search(
        pattern=inject.give_pattern, string=gml.split(INJECTION_START_MARKER)[0]
    )


def _add_inject_gmls_in_script(script: str, dependency_gmls: List[str]) -> str:
    """Returns the script after supplying dependencies."""
    script_content = _get_script_contents(script)
    new_script = script_content
    if dependency_gmls:
        injection_gml = "\n\n".join(dependency_gmls)
        new_script += f"""\


{INJECTION_START_HEADER}
{injection_gml}
{INJECTION_END_HEADER}"""
    return new_script


def _get_script_contents(script: str):
    """Get the portion of the script above the dependency header."""
    return script.split(INJECTION_START_MARKER)[0].rstrip()
