import abc
from pathlib import Path

from rivals_workshop_assistant.script_mod import Script


def handle_warning(assistant_config: dict, scripts: list[Script]):
    warning_types = get_warning_types(assistant_config)
    for script in scripts:
        if script.is_fresh:
            _apply_warnings_to_script(script, warning_types)


class WarningType(abc.ABC):
    pass

    def apply(self, script: Script):
        raise NotImplementedError


def get_warning_types(assistant_config: dict) -> set[WarningType]:
    raise NotImplementedError


def _apply_warnings_to_script(script: Script, warning_types: set[WarningType]):
    _remove_warnings(script)
    for warning_type in warning_types:
        _apply_warning_to_script(script, warning_type)


def _remove_warnings(script: Script):
    raise NotImplementedError


def _apply_warning_to_script(script: Script, warning_type: WarningType):
    warning_type.apply(script)
