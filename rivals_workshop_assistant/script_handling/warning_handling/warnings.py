import itertools
from typing import Set

from loguru import logger

from rivals_workshop_assistant import assistant_config_mod as config_mod
from rivals_workshop_assistant.script_handling.warning_handling.base import WarningType
from rivals_workshop_assistant.script_handling.warning_handling import (
    desync,
    set_attack,
)
from rivals_workshop_assistant.script_handling.warning_handling import hitpause

warning_names_to_types = {
    config_mod.WARNING_DESYNC_OBJECT_VAR_SET_IN_DRAW_SCRIPT_VALUE: [
        desync.ObjectVarSetInDrawScript()
    ],
    config_mod.WARNING_DESYNC_UNSAFE_CAMERA_READ_VALUE: [
        desync.UnsafeCameraReadX(),
        desync.UnsafeCameraReadY(),
    ],
    config_mod.WARNING_CHECK_WINDOW_TIMER_WITHOUT_CHECK_HITPAUSE: [
        hitpause.CheckWindowTimerEqualsWithoutCheckHitpause(),
        hitpause.CheckWindowTimerModuloWithoutCheckHitpause(),
    ],
    config_mod.WARNING_RECURSIVE_SET_ATTACK: [set_attack.RecursiveSetAttack()],
}


def get_warning_types(assistant_config: dict) -> Set[WarningType]:
    try:
        return set(
            itertools.chain(
                *(
                    types
                    for key, types in warning_names_to_types.items()
                    if key in assistant_config.get(config_mod.WARNINGS_FIELD, [])
                )
            )
        )
    except (KeyError, TypeError):
        logger.warning(
            f"assistant config's {config_mod.WARNINGS_FIELD} value is invalid. "
            f"Should be a list. "
            f"Got: {assistant_config.get(config_mod.WARNINGS_FIELD, [])}"
        )
        return set()
