import typing
from typing import List

from .application import apply_injection
from .library import read_injection_library

from rivals_workshop_assistant.aseprite_handling import Anim
from rivals_workshop_assistant.dotfile_mod import get_clients_for_injection
from rivals_workshop_assistant.run_context import RunContext

if typing.TYPE_CHECKING:
    from rivals_workshop_assistant.script_handling.script_mod import Script


def handle_injection(
    run_context: RunContext, scripts: list["Script"], anims: List[Anim]
):
    """Controller"""
    injection_library = read_injection_library(run_context.root_dir)
    apply_injection(
        scripts=scripts,
        injection_library=injection_library,
        anims=anims,
        dotfile=run_context.dotfile,
    )


def freshen_scripts_that_have_modified_dependencies(
    dotfile: dict, scripts, inject_scripts: list["Script"]
):
    """Sets each script with modified dependencies to be considered freshly changed"""

    for inject_script in inject_scripts:
        if inject_script.is_fresh:
            # if an inject file has changed, mark its clients for update
            clients = get_clients_for_injection(
                dotfile=dotfile, injection_script=inject_script.path
            )
            for script in scripts:
                if script.path in clients:
                    script.file_is_fresh = True
