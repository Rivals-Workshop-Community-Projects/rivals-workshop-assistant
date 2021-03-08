from pathlib import Path

from .application import apply_injection
from .dependency_handling import GmlInjection
from .library import read_injection_library
from ..scripts_type import Scripts


def handle_injection(root_dir: Path, scripts: Scripts):
    injection_library = read_injection_library(root_dir)
    result_scripts = apply_injection(scripts, injection_library)
    return result_scripts
