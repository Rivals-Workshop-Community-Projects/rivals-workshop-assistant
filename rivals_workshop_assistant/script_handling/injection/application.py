import re
import typing
from typing import List

from .dependency_handling import GmlInjection
from rivals_workshop_assistant.dotfile_mod import update_all_dotfile_injection_clients
from rivals_workshop_assistant.aseprite_handling import Anim

if typing.TYPE_CHECKING:
    from rivals_workshop_assistant.script_handling.script_mod import Script

OLD_INJECTION_START_MARKERS = ["// vvv LIBRARY DEFINES AND MACROS vvv\n"]
INJECTION_START_MARKER = "// #region vvv LIBRARY DEFINES AND MACROS vvv\n"
INJECTION_START_WARNING = (
    "// DANGER File below this point will be overwritten! "
    "Generated defines and macros below.\n"
    "// Write NO-INJECT in a comment above this area to disable injection."
)
OLD_INJECTION_START_HEADERS = [
    f"{start}{INJECTION_START_WARNING}" for start in OLD_INJECTION_START_MARKERS
]
INJECTION_START_HEADER = f"{INJECTION_START_MARKER}{INJECTION_START_WARNING}"
INJECTION_END_HEADER = (
    "// DANGER: "
    "Write your code ABOVE the LIBRARY DEFINES AND MACROS header "
    "or it will be overwritten!\n"
    "// #endregion"
)


def apply_injection(
    scripts: List["Script"],
    injection_library: List[GmlInjection],
    anims: List[Anim],
    dotfile: dict = None,
):
    """Updates scripts with supplied dependencies."""
    for script in scripts:
        anim = _get_anim_for_script(script, anims)
        if script.is_fresh or (anim is not None and anim.is_fresh):
            _apply_injection_to_script(script, injection_library, anim, dotfile)


def _apply_injection_to_script(
    script: "Script",
    injection_library: List[GmlInjection],
    anim: Anim,
    dotfile: dict = None,
):
    """Updates the dependencies supplied to the script."""
    if _should_inject(script.working_content):

        needed_injects = _get_injects_needed_in_gml(
            gml=_get_script_contents(script.working_content),
            injection_library=injection_library,
        )
        update_all_dotfile_injection_clients(
            dotfile=dotfile,
            needed_injects=needed_injects,
            script=script,
        )

        needed_gmls = [
            injection.gml for injection in needed_injects
        ] + _get_anim_data_gmls_needed_in_gml(anim)

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


def _get_anim_for_script(script: "Script", anims: List[Anim]) -> typing.Optional[Anim]:
    # TODO If we have access to the dotfile here, we can look up in the anim hashes which aseprite an anim belongs to
    #   and then we can only load that aseprite's anims
    if script.path.parent.name != "attacks":
        return None
    for anim in anims:
        cleaned_name = anim.name.replace("HURTBOX", "").strip()
        if cleaned_name == script.path.stem:
            return anim
    return None


def _get_injects_needed_in_gml(
    gml: str, injection_library: List[GmlInjection]
) -> List[GmlInjection]:
    used_injects = _get_injects_used_in_gml(gml, injection_library)
    needed_injects = [inject for inject in used_injects if not inject.is_given(gml)]
    return needed_injects


def _get_injects_used_in_gml(
    gml: str,
    injection_library: List[GmlInjection],
    existing_injections: List[GmlInjection] = None,
) -> List[GmlInjection]:
    if existing_injections is None:
        injections = []  # could be set but constant order is nice
    else:
        injections = existing_injections

    for injection in injection_library:
        if injection not in injections and injection.is_used(gml):
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
    old_markers_pattern = "|".join(marker for marker in OLD_INJECTION_START_MARKERS)
    pattern = rf"(?:{INJECTION_START_MARKER}|{old_markers_pattern})"
    contents = re.split(pattern=pattern, string=script)[0].rstrip()
    return contents
