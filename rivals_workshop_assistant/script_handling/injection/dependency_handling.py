import abc
import string
import textwrap
from typing import List, Tuple, Union
from pathlib import Path


class GmlInjection(abc.ABC):
    def __init__(
        self,
        name: str,
        gml: str,
        use_pattern: str,
        give_pattern: str,
        filepath: Path = None,
    ):
        self.name = name
        self.gml = gml
        self.use_pattern = use_pattern
        self.give_pattern = give_pattern
        self.filepath = filepath

    def is_used(self, gml):
        raise NotImplementedError

    def is_given(self, gml):
        raise NotImplementedError

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.gml == other.gml
            and self.use_pattern == other.use_pattern
            and self.give_pattern == other.give_pattern
        )

    def __hash__(self):
        return hash(self.name)


class GmlDeclaration(GmlInjection, abc.ABC):
    IDENTIFIER_STRING = NotImplemented

    def __init__(self, name: str, gml: str, use_pattern: str, filepath: Path = None):
        """Serialize the gml elements into the final gml structure."""
        super().__init__(
            name=name,
            gml=gml,
            give_pattern=fr"#{self.IDENTIFIER_STRING}(\s)*{name}(\W|$)",
            use_pattern=use_pattern,
            filepath=filepath,
        )

    @classmethod
    @abc.abstractmethod
    def from_gml(cls, name: str, content: str, filepath: Path = None):
        raise NotImplementedError


class Define(GmlDeclaration):
    IDENTIFIER_STRING = "define"

    def __init__(
        self,
        name: str,
        content: str,
        version: int = 0,
        docs: str = "",
        params: List[str] = None,
        filepath: Path = None,
    ):
        if params is None:
            params = []
        if params:
            param_string = f"({', '.join(params)})"
        else:
            param_string = ""

        self.docs = docs  # I think this might only apply to defines?

        head = f"#{self.IDENTIFIER_STRING} {name}{param_string}"
        if docs.strip():
            docs = textwrap.indent(textwrap.dedent(docs), "    // ") + "\n"

        content = textwrap.indent(textwrap.dedent(content), "    ")

        final = f"{head} // Version {version}\n{docs}{content}"
        gml = textwrap.dedent(final).strip()
        use_pattern = fr"(?<!#define)(^|\W){name}\("
        super().__init__(
            name,
            gml,
            use_pattern=use_pattern,
            filepath=filepath,
        )

    def is_used(self, gml):
        use_splits = gml.split(f"{self.name}(")
        # range len is clearer than enumerate here I think
        for first_i in range(len(use_splits) - 1):
            is_usage = (
                _prev_char_is_terminator(use_splits[first_i])
            ) and not use_splits[first_i].endswith("#define ")
            if is_usage:
                return True
        return False

    def is_given(self, gml):
        use_splits = gml.split(f"#define {self.name}")
        for first_i in range(len(use_splits) - 1):
            is_usage = _next_char_is_terminator(use_splits[first_i + 1])
            if is_usage:
                return True
        return False

    @classmethod
    def from_gml(cls, name: str, content: str, filepath: Path = None):
        content = _remove_brackets(content)
        content = textwrap.dedent(content).strip("\n")
        docs, content = _split_docs_and_gml(content)
        name, params = _split_name_and_params(name)
        return cls(
            name=name, params=params, docs=docs, content=content, filepath=filepath
        )


class Comment(str):
    pass


def _partition_block_comments(content: str) -> List[Union[str, Comment]]:
    partitions = []
    start_splits = content.split("/*")

    partitions.append(start_splits[0])
    for start_split in start_splits[1:]:
        end_splits = start_split.split("*/")
        comment, code = end_splits
        partitions.append(Comment(comment))
        partitions.append(code)
    return partitions


def _normalize_block_comments(content: str) -> str:
    """Add // to the beginning of all lines inside a /* */ block"""

    comment_partitions = _partition_block_comments(content)
    normalized_partitions = []
    for partition in comment_partitions:
        if isinstance(partition, Comment):
            comment = partition
            normalized_comment_lines = []
            comment_lines = comment.splitlines(keepends=True)
            normalized_comment_lines.append(comment_lines[0])
            for line in comment_lines[1:]:
                if line.lstrip().startswith("//"):
                    normalized_line = line
                else:
                    normalized_line = f"// {line}"
                normalized_comment_lines.append(normalized_line)
            normalized_comment = f'/*{"".join(normalized_comment_lines)}*/'
            normalized_partitions.append(normalized_comment)
        else:
            normalized_partitions.append(partition)

    normalized_content = "".join(normalized_partitions)
    return normalized_content


def _is_content_line(line: str, remove_comments=False) -> bool:
    stripped = line.strip()
    is_empty = len(stripped) == 0

    if remove_comments:
        is_comment = any(
            stripped.startswith(comment_str) for comment_str in ("//", "/*", "*/")
        )
        return not (is_empty or is_comment)
    else:
        return not is_empty


def _strip_content_in_direction(
    content: str, remove_comments: bool = False, reverse: bool = False
) -> str:
    stripped_lines = []

    lines = content.splitlines()
    if reverse:
        lines = reversed(lines)

    content_found = False
    for line in lines:
        if content_found:
            stripped_lines.append(line)
        else:
            if _is_content_line(line, remove_comments):
                content_found = True
                stripped_lines.append(line)

    if reverse:
        stripped_lines = reversed(stripped_lines)

    stripped_content = "\n".join(stripped_lines)
    return stripped_content


def _strip_non_content_lines(content: str) -> str:
    """Remove surrounding whitespace, empty lines, and comment lines"""
    content = _strip_content_in_direction(content)
    content = _strip_content_in_direction(content, remove_comments=True, reverse=True)
    return content


def _remove_brackets(content):
    has_start_bracket = content.strip().startswith("{")
    has_end_bracket = content.strip().endswith("}")
    if (has_start_bracket and not has_end_bracket) or (
        content.count("{") != content.count("}")
    ):
        raise ValueError(f"Mismatched curly braces at:\n{content}\n\n---\n")
    if has_start_bracket and has_end_bracket:
        content = content.strip().lstrip("{").rstrip("}").strip("\n")
    return content


def _split_docs_and_gml(content: str) -> Tuple[str, str]:
    lines = content.split("\n")
    non_docs_found = False

    doc_lines = []
    gml_lines = []
    for line in lines:
        if not non_docs_found:
            if line.lstrip().startswith("//"):
                line = line.split("//")[1].rstrip()
                if line[0] == " ":  # Remove padding from '// ' format
                    line = line[1:]
                doc_lines.append(line)
                continue
            else:
                non_docs_found = True
        gml_lines.append(line.rstrip())

    return "\n".join(doc_lines), "\n".join(gml_lines)


def _split_name_and_params(name: str) -> Tuple[str, List[str]]:
    name = name.strip()
    if "(" not in name:
        return name, []
    else:
        if not name.endswith(")"):
            raise ValueError(f"Missing ) for parameter line: {name}")
        name, param_string = name.rstrip(")").split("(")
        params = [param.strip() for param in param_string.split(",") if param]
        return name, params


class Macro(GmlDeclaration):
    IDENTIFIER_STRING = "macro"

    def __init__(self, name: str, value: str, filepath: Path = None):
        gml = f"#macro {name} {value}"
        super().__init__(
            name,
            gml,
            use_pattern=fr"(^|\W){name}($|\W)",
            filepath=filepath,
        )

    def is_used(self, gml):
        use_splits = gml.split(f"{self.name}")
        for first_i in range(len(use_splits) - 1):
            is_usage = (
                _prev_char_is_terminator(use_splits[first_i])
                and _next_char_is_terminator(use_splits[first_i + 1])
                and not use_splits[first_i].endswith("#macro ")  # Isn't a definition
            )
            if is_usage:
                return True
        return False

    def is_given(self, gml):
        use_splits = gml.split(f"#macro {self.name}")
        for first_i in range(len(use_splits) - 1):
            is_usage = _next_char_is_terminator(use_splits[first_i + 1])
            if is_usage:
                return True
        return False

    @classmethod
    def from_gml(cls, name: str, content: str, filepath: Path = None):
        if content[0] == " ":
            content = content[1:]  # remove leading space

        content = textwrap.dedent(content).strip("\n")
        content = "\n".join(line.rstrip() for line in content.split("\n"))

        return cls(name=name, value=content, filepath=filepath)


INJECT_TYPES = (Define, Macro)


def _char_is_token_terminator(char: str):
    return char.isspace() or (char != "_" and char in string.punctuation)


def _prev_char_is_terminator(split):
    if split:
        prev_char = split[-1]
        return _char_is_token_terminator(prev_char)
    else:
        return True


def _next_char_is_terminator(split):
    if split:
        prev_char = split[0]
        return _char_is_token_terminator(prev_char)
    else:
        return True
