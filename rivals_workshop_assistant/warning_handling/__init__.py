import abc
import re
from pathlib import Path

from rivals_workshop_assistant.script_mod import Script

WARNING_PREFIX = "// WARN: "


def handle_warning(assistant_config: dict, scripts: list[Script]):
    warning_types = get_warning_types(assistant_config)
    for script in scripts:
        if script.is_fresh:
            _apply_warnings_to_script(script, warning_types)


class WarningType(abc.ABC):
    warning_text = NotImplemented

    def _should_warn_for_line(self, script: Script, line: str) -> bool:
        raise NotImplementedError

    def apply(self, script: Script):
        detection_lines = self.get_detection_lines(script)
        script.working_content = self.write_warning(
            detection_lines=detection_lines, gml=script.working_content
        )

    def get_detection_lines(self, script: Script):
        detection_lines = []
        for number, line in enumerate(script.working_content.splitlines()):
            if self._should_warn_for_line(script, line):
                detection_lines.append(number)
        return detection_lines

    def write_warning(self, detection_lines: list[int], gml: str) -> str:
        lines = gml.split("\n")
        for line_num in detection_lines:
            lines[line_num] += self.make_warning_text()
        return "\n".join(lines)

    def make_warning_text(self) -> str:
        return WARNING_PREFIX + self.warning_text


class PossibleDesyncWarning(WarningType):
    warning_text = "Possible Desync. Non-local var set in draw script."

    def get_detection_lines(self, script: Script):
        if not is_draw_script(script.path):
            return []
        detection_lines = []
        local_vars = []
        for number, line in enumerate(script.working_content.splitlines()):

            var_split = line.split("var")
            if var_split[1:]:
                local_vars.append(var_split[1].lstrip().split()[0])

            if self._should_warn_for_line(local_vars=local_vars, line=line):
                detection_lines.append(number)
        return detection_lines

    def _should_warn_for_line(self, local_vars: list[str], line: str) -> bool:
        # A variable is set without 'var', and it is not in the list of local_vars
        pattern = fr'^\s*(?!(?:{"|".join(local_vars)}))\w+\s*(=|\+=|-=|\*=|\/=)\s*\S'
        return re.match(pattern=pattern, string=line) is not None


def is_draw_script(path: Path) -> bool:
    return path.stem.endswith("_draw") or path.stem in ["init_shader", "draw_hud"]


def get_warning_types(assistant_config: dict) -> set[WarningType]:
    return {PossibleDesyncWarning()}


def _apply_warnings_to_script(script: Script, warning_types: set[WarningType]):
    script.working_content = _remove_warnings(script.working_content)
    for warning_type in warning_types:
        _apply_warning_to_script(script, warning_type)


def _remove_warnings(script_content: str) -> str:
    return re.sub(pattern=r"//WARN:.*(\n|$)", repl="\n", string=script_content)


def _apply_warning_to_script(script: Script, warning_type: WarningType):
    warning_type.apply(script)
