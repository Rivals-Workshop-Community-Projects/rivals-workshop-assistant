from pathlib import Path

from .application import apply_injection
from .library import read_injection_library
from rivals_workshop_assistant.script_mod import Script
from ..aseprite_handling import Anim


def handle_injection(root_dir: Path, scripts: list[Script], anims: list[Anim]):
    """Controller"""
    injection_library = read_injection_library(root_dir)
    result_scripts = apply_injection(scripts, injection_library, anims)
    return result_scripts
