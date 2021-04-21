from pathlib import Path

from .installation import update_injection_library
from .application import apply_injection
from .library import read_injection_library
from rivals_workshop_assistant.script_mod import Script


def handle_injection(
    root_dir: Path, dotfile: dict, assistant_config: dict, scripts: list[Script]
):
    """Controller"""
    update_injection_library(root_dir, dotfile=dotfile, config=assistant_config)
    injection_library = read_injection_library(root_dir)
    result_scripts = apply_injection(scripts, injection_library)
    return result_scripts
