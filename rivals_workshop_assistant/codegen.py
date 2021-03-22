from rivals_workshop_assistant.paths import Scripts


def handle_codegen(scripts: Scripts):
    codegen_library = read_codegen_library()  # Hardcode this stuff in python,
    # not fs
    result_scripts = apply_codegen(scripts, codegen_library)
    return result_scripts


def read_codegen_library():
    raise NotImplementedError


def apply_codegen(scripts: Scripts, codegen_library):
    # Logic
    raise NotImplementedError
