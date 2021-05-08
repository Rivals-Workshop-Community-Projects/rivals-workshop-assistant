import abc
from pathlib import Path

from rivals_workshop_assistant.script_mod import Script

WARNING_PREFIX = " // WARN: "


class WarningType(abc.ABC):
    warning_content = NotImplemented

    def _should_warn_for_line(self, script: Script, line: str) -> bool:
        raise NotImplementedError

    def apply(self, script: Script):
        if not self._should_apply_to_script(script):
            return []

        detection_lines = self.get_detection_lines(script)
        script.working_content = self.write_warning(
            detection_lines=detection_lines, gml=script.working_content
        )

        # This is just for debugging purposes
        return [
            line
            for i, line in enumerate(script.working_content.splitlines())
            if i in detection_lines
        ]

    def get_detection_lines(self, script: Script):
        detection_lines = []
        for number, line in enumerate(script.working_content.splitlines()):
            if not is_line_suppressed(line) and self._should_warn_for_line(
                script, line
            ):
                detection_lines.append(number)
        return detection_lines

    def write_warning(self, detection_lines: list[int], gml: str) -> str:
        lines = gml.split("\n")
        for line_num in detection_lines:
            lines[line_num] += self.warning_text
        return "\n".join(lines)

    @classmethod
    @property
    def warning_text(cls) -> str:
        return WARNING_PREFIX + cls.warning_content

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def __hash__(self):
        return hash(self.__class__)

    def _should_apply_to_script(self, script: Script):
        return True


def is_line_suppressed(line: str):
    return "NO-WARN" in line.upper()


def is_draw_script(path: Path) -> bool:
    return path.stem.endswith("_draw") or path.stem in ["init_shader", "draw_hud"]
