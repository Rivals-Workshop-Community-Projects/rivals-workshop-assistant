import re

from rivals_workshop_assistant.script_mod import Script
from rivals_workshop_assistant.warning_handling.base import (
    WarningType,
    is_line_suppressed,
    is_draw_script,
)


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
