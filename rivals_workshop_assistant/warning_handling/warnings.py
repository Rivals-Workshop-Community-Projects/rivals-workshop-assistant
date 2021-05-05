import abc
import itertools
import re
from pathlib import Path

from rivals_workshop_assistant import assistant_config_mod as config_mod
from rivals_workshop_assistant.script_mod import Script

WARNING_PREFIX = " // WARN: "


class WarningType(abc.ABC):
    warning_content = NotImplemented

    def _should_warn_for_line(self, script: Script, line: str) -> bool:
        raise NotImplementedError

    def apply(self, script: Script):
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


def is_line_suppressed(line: str):
    return "NO-WARN" in line.upper()


class ObjectVarSetInDrawScript(WarningType):
    warning_content = (
        "Possible Desync. Object var set in draw script."
        " Consider using `var` or creating constants in `init.gml`."
    )

    def get_detection_lines(self, script: Script):
        if not is_draw_script(script.path):
            return []
        detection_lines = []
        local_vars = []
        for number, line in enumerate(script.working_content.splitlines()):
            local_vars_in_line = re.findall(pattern=r"(?<=var )\w+", string=line)
            local_vars += local_vars_in_line

            if not is_line_suppressed(line) and self._should_warn_for_line(
                local_vars=local_vars, line=line
            ):
                detection_lines.append(number)
        return detection_lines

    def _should_warn_for_line(self, local_vars: list[str], line: str) -> bool:
        # A variable is set without 'var', and it is not in the list of local_vars
        pattern = fr'^\s*(?!(?:{"|".join(["var"] + local_vars)}))\w+\s*(=|\+=|-=|\*=|\/=)\s*\S'
        return re.search(pattern=pattern, string=line) is not None


class UnsafeCameraReadX(WarningType):
    warning_content = (
        'Possible Desync. Consider using get_instance_x(asset_get("camera_obj")).'
    )

    def _should_warn_for_line(self, script: Script, line: str) -> bool:
        return "view_get_xview(" in line


class UnsafeCameraReadY(WarningType):
    warning_content = (
        'Possible Desync. Consider using get_instance_y(asset_get("camera_obj")).'
    )

    def _should_warn_for_line(self, script: Script, line: str) -> bool:
        return "view_get_yview(" in line


def is_draw_script(path: Path) -> bool:
    return path.stem.endswith("_draw") or path.stem in ["init_shader", "draw_hud"]


warning_names_to_types = {
    config_mod.WARNING_DESYNC_OBJECT_VAR_SET_IN_DRAW_SCRIPT_VALUE: [
        ObjectVarSetInDrawScript()
    ],
    config_mod.WARNING_DESYNC_UNSAFE_CAMERA_READ_VALUE: [
        UnsafeCameraReadX(),
        UnsafeCameraReadY(),
    ],
}


def get_warning_types(assistant_config: dict) -> set[WarningType]:
    return set(
        itertools.chain(
            *(
                types
                for key, types in warning_names_to_types.items()
                if key in assistant_config.get(config_mod.WARNINGS_FIELD, [])
            )
        )
    )
