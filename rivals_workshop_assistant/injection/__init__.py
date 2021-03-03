from .application import apply_injection
from .dependencies import GmlDependency


def handle_injection(scripts):
    injection_library = read_injection_library()
    result_scripts = apply_injection(scripts, injection_library)
    return result_scripts


def read_injection_library():
    raise NotImplementedError
    # Get library path
    # If not exists, create and populate from a cdn I'll have to make.
    # Read files to text

    # Read text to injection_library: list of dependencies


