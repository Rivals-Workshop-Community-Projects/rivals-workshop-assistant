import abc
import re
import textwrap
import typing as t
from pathlib import Path


class GmlDependency(abc.ABC):
    def __init__(self,
                 name: str,
                 gml: str,
                 use_pattern: str = None,
                 give_pattern: str = None
                 ):
        self.name = name
        self.gml = gml
        self.use_pattern = use_pattern
        self.give_pattern = give_pattern

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


class GmlDeclaration(GmlDependency, abc.ABC):
    IDENTIFIER_STRING = NotImplemented

    def __init__(
            self,
            name: str,
            gml: str,
    ):
        """Serialize the gml elements into the final gml structure."""
        super().__init__(
            name=name,
            gml=gml,
            use_pattern=fr"(^|\W){name}\(",
            give_pattern=fr'{self.IDENTIFIER_STRING}(\s)*{name}(\W|$)',
        )


class Define(GmlDeclaration):
    IDENTIFIER_STRING = '#define'

    def __init__(
            self,
            name: str,
            version: int,
            docs: str,
            content: str,
            params: t.List[str] = None,
    ):

        if params is None:
            params = []
        if params:
            param_string = f"({', '.join(params)})"
        else:
            param_string = ''

        head = f"{self.IDENTIFIER_STRING} {name}{param_string}"
        docs = textwrap.indent(textwrap.dedent(docs), '    // ')
        content = textwrap.indent(textwrap.dedent(content), '    ')

        final = f"{head} // Version {version}\n{docs}\n{content}"
        gml = textwrap.dedent(final).strip()

        super().__init__(name, gml)


class Macro(GmlDeclaration):  # todo untested
    IDENTIFIER_STRING = '#macro'


def handle_injection(scripts):
    injection_library = read_injection_library()
    result_scripts = apply_injection(scripts, injection_library)
    return result_scripts


def read_injection_library():
    raise NotImplementedError


INJECTION_START_HEADER = '// vvv LIBRARY DEFINES AND MACROS vvv'
INJECTION_END_HEADER = '// ^^^ END: LIBRARY DEFINES AND MACROS ^^^'


def apply_injection(scripts: t.Dict[Path, str], injection_library: t.List[GmlDependency]) -> t.Dict[Path, str]:
    """Creates a new scripts collection where each script has updated supplied dependencies."""
    result_scripts = scripts.copy()
    for path, script in scripts.items():
        result_scripts[path] = apply_injection_to_script(script, injection_library)

    return result_scripts


def apply_injection_to_script(script: str, injection_library: t.List[GmlDependency]) -> str:
    """Updates the dependencies supplied to the script."""
    dependency_gmls = get_dependency_gmls_used_in_script(script, injection_library)
    return inject_dependency_gmls_in_script(script, dependency_gmls)


def get_dependency_gmls_used_in_script(script: str, injection_library: t.List[GmlDependency]) -> t.List[str]:
    """Gets the gml content of each dependency used by the script."""
    dependency_gmls = []
    for injection in injection_library:
        if re.search(pattern=injection.use_pattern, string=script):
            dependency_gmls.append(injection.gml)
    return dependency_gmls


def inject_dependency_gmls_in_script(script: str, dependency_gmls: t.List[str]) -> str:
    """Returns the script after supplying dependencies."""
    script_content = script.split(INJECTION_START_HEADER)[0].strip()
    new_script = script_content
    if dependency_gmls:
        injection_gml = '\n\n'.join(dependency_gmls)
        new_script += f"""\


{INJECTION_START_HEADER}
{injection_gml}
{INJECTION_END_HEADER}"""
    return new_script
