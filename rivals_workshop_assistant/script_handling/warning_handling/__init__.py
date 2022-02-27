import re

from rivals_workshop_assistant.script_handling.warning_handling.warnings import (
    get_warning_types,
)
from rivals_workshop_assistant.script_handling.warning_handling.base import (
    WARNING_PREFIX,
    WarningType,
)
from rivals_workshop_assistant.script_handling.script_mod import Script


def handle_warning(assistant_config: dict, scripts: list[Script]):
    warning_types = get_warning_types(assistant_config)
    for script in scripts:
        if script.is_fresh:
            _apply_warnings_to_script(script, warning_types)


def _apply_warnings_to_script(script: Script, warning_types: set[WarningType]):
    script.working_content = remove_warnings(script.working_content)
    for warning_type in warning_types:
        _apply_warning_to_script(script, warning_type)


def remove_warnings(script_content: str) -> str:
    stripped = re.sub(
        pattern=fr"{WARNING_PREFIX}.*(\n|$)", repl="\n", string=script_content
    )
    return stripped


def _apply_warning_to_script(script: Script, warning_type: WarningType):
    warning_type.apply(script)
