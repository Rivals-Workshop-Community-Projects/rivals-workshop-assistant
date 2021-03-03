import abc
import textwrap
import typing as t


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
