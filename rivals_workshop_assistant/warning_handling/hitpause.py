import abc
import re

from rivals_workshop_assistant.script_mod import Script
from rivals_workshop_assistant.warning_handling.base import (
    is_line_suppressed,
    WarningType,
)


class ABCHitpauseWarning(WarningType, abc.ABC):
    def get_detection_lines(self, script: Script):
        detection_lines = []
        guard_seen = False
        for number, line in enumerate(script.working_content.splitlines()):
            if _is_hitpause_guard(line):
                guard_seen = True
            if (
                not guard_seen
                and not is_line_suppressed(line)
                and self._should_warn_for_line(script=script, line=line)
            ):
                detection_lines.append(number)
        return detection_lines


NOT_HITPAUSE = "!hitpause"


class CheckWindowTimerEqualsWithoutCheckHitpause(ABCHitpauseWarning):
    warning_content = "Possible repetition during hitpause. Consider using window_time_is(frame) https://rivalslib.com/assistant/function_library/attacks/window_time_is.html"

    def _should_warn_for_line(self, script: Script, line: str) -> bool:
        return _has_window_timer_eq_check(line) and not NOT_HITPAUSE in line


def _is_hitpause_guard(line: str) -> bool:
    return NOT_HITPAUSE in line and "window_timer" not in line


def _has_window_timer_eq_check(line: str) -> bool:
    pattern = r"^\s*if.*(= window_timer\s*|\s*window_timer\s*=)"
    return re.search(pattern=pattern, string=line) is not None


class CheckWindowTimerModuloWithoutCheckHitpause(ABCHitpauseWarning):
    warning_content = "Possible repetition during hitpause. Consider using window_time_is_div(frame) https://rivalslib.com/assistant/function_library/attacks/window_time_is_div.html"

    def _should_warn_for_line(self, script: Script, line: str) -> bool:
        return _has_window_timer_mod_check(line) and not NOT_HITPAUSE in line


def _has_window_timer_mod_check(line: str) -> bool:
    pattern = r"^\s*if.*window_timer\s*%\s*\S+\s*==?\s*0"
    return re.search(pattern=pattern, string=line) is not None
