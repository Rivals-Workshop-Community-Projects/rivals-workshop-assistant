import re

from rivals_workshop_assistant.script_mod import Script
from rivals_workshop_assistant.warning_handling.warnings import (
    WarningType,
    get_warning_types,
    WARNING_PREFIX,
)


def handle_warning(assistant_config: dict, scripts: list[Script]):
    warning_types = get_warning_types(assistant_config)
    for script in scripts:
        if script.is_fresh:
            _apply_warnings_to_script(script, warning_types)


def _apply_warnings_to_script(script: Script, warning_types: set[WarningType]):
    script.working_content = _remove_warnings(script.working_content)
    for warning_type in warning_types:
        _apply_warning_to_script(script, warning_type)


def _remove_warnings(script_content: str) -> str:
    return re.sub(
        pattern=fr"{WARNING_PREFIX}:.*(\n|$)", repl="\n", string=script_content
    )


def _apply_warning_to_script(script: Script, warning_type: WarningType):
    warning_type.apply(script)
