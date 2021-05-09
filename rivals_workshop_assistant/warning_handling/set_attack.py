from rivals_workshop_assistant.script_mod import Script
from rivals_workshop_assistant.warning_handling.base import WarningType


class RecursiveSetAttack(WarningType):
    warning_content = "Risk of crash. in `attack_set.gml` you can just write `attack = x` instead of `set_attack(x)`."

    def _should_apply_to_script(self, script: Script):
        return script.path.stem == "set_attack"

    def _should_warn_for_line(self, script: Script, line: str) -> bool:
        return "set_attack(" in line
