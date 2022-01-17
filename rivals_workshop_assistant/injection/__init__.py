from pathlib import Path
from typing import List

from .application import apply_injection
from .library import read_injection_library
from rivals_workshop_assistant.script_mod import Script
from ..aseprite_handling import Anim
from ..dotfile_mod import get_clients_for_injection


def handle_injection(
    root_dir: Path, scripts: List[Script], anims: List[Anim], dotfile: dict = None
):
    """Controller"""
    injection_library = read_injection_library(root_dir)
    apply_injection(scripts, injection_library, anims, dotfile)


def freshen_scripts_with_modified_dependencies(
    dotfile: dict, scripts, inject_scripts: List[Script]
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
