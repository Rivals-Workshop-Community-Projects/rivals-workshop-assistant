from pathlib import Path
from typing import List

from .application import apply_injection
from .library import read_injection_library
from rivals_workshop_assistant.script_mod import Script
from ..aseprite_handling import Anim


def handle_injection(root_dir: Path, scripts: List[Script], anims: List[Anim]):
    """Controller"""
    injection_library = read_injection_library(root_dir)
    apply_injection(scripts, injection_library, anims)
