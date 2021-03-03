def handle_codegen(scripts):
    codegen_library = read_codegen_library()
    result_scripts = apply_codegen(scripts, codegen_library)
    return result_scripts


def read_codegen_library():
    raise NotImplementedError


def apply_codegen(scripts, codegen_library):
    # Logic
    raise NotImplementedError