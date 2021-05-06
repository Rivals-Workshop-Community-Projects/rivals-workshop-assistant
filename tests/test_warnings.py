from pathlib import Path

import pytest

import rivals_workshop_assistant.warning_handling.desync
import rivals_workshop_assistant.warning_handling.hitpause
import rivals_workshop_assistant.warning_handling.warnings as src
from rivals_workshop_assistant.assistant_config_mod import (
    WARNINGS_FIELD,
    WARNING_DESYNC_OBJECT_VAR_SET_IN_DRAW_SCRIPT_VALUE,
)
from tests.testing_helpers import make_script


def test_get_warning_types():
    config = {WARNINGS_FIELD: [WARNING_DESYNC_OBJECT_VAR_SET_IN_DRAW_SCRIPT_VALUE]}

    result = src.get_warning_types(config)

    assert result == {
        rivals_workshop_assistant.warning_handling.desync.ObjectVarSetInDrawScript()
    }


@pytest.mark.parametrize(
    "path, original_content, expected_content",
    [
        pytest.param("post_draw", "nothing to do", "nothing to do"),
        pytest.param(
            "post_draw",
            "global = 3",
            f"global = 3{rivals_workshop_assistant.warning_handling.desync.ObjectVarSetInDrawScript.warning_text}",
        ),
        pytest.param(
            "post_draw",
            "okay line\nglobal = 3\nalso fine",
            f"okay line\nglobal = 3{rivals_workshop_assistant.warning_handling.desync.ObjectVarSetInDrawScript.warning_text}\nalso fine",
        ),
        pytest.param(
            "post_draw",
            "var a = 3",
            f"var a = 3",
        ),
        pytest.param(
            "post_draw",
            "var a = 3\na = 4",
            f"var a = 3\na = 4",
        ),
        pytest.param(
            "post_draw",
            "var a = 3\na = 4",
            f"var a = 3\na = 4",
        ),
        pytest.param(
            "update",
            "a = 3",
            f"a = 3",
        ),
        pytest.param(
            "post_draw",
            "a += 3",
            f"a += 3{rivals_workshop_assistant.warning_handling.desync.ObjectVarSetInDrawScript.warning_text}",
        ),
        pytest.param(
            "post_draw",
            "a += 3   // NO-WARN",
            "a += 3   // NO-WARN",
        ),
    ],
)
def test_handle_warn_setting_nonlocal_var_in_draw_script(
    path, original_content, expected_content
):
    path = Path(path + ".gml")
    script = make_script(path=path, original_content=original_content)
    sut = rivals_workshop_assistant.warning_handling.desync.ObjectVarSetInDrawScript()

    sut.apply(script)

    assert script == make_script(
        path, original_content=original_content, working_content=expected_content
    )


@pytest.mark.parametrize(
    "path, original_content, expected_content",
    [
        pytest.param("post_draw", "nothing to do", "nothing to do"),
        pytest.param(
            "post_draw",
            f"if window_timer == 3",
            f"if window_timer == 3{rivals_workshop_assistant.warning_handling.hitpause.CheckWindowTimerEqualsWithoutCheckHitpause.warning_text}",
        ),
        pytest.param(
            "post_draw",
            f"if window_timer = 3",
            f"if window_timer = 3{rivals_workshop_assistant.warning_handling.hitpause.CheckWindowTimerEqualsWithoutCheckHitpause.warning_text}",
        ),
        pytest.param(
            "post_draw",
            f"if (window_timer == 3)",
            f"if (window_timer == 3){rivals_workshop_assistant.warning_handling.hitpause.CheckWindowTimerEqualsWithoutCheckHitpause.warning_text}",
        ),
        pytest.param(
            "post_draw",
            f" if   (  window_timer   ==    3  )",
            f" if   (  window_timer   ==    3  ){rivals_workshop_assistant.warning_handling.hitpause.CheckWindowTimerEqualsWithoutCheckHitpause.warning_text}",
        ),
        pytest.param(
            "post_draw",
            f"if !hitpause\nif window_timer == 3",
            f"if !hitpause\nif window_timer == 3",
        ),
    ],
)
def test_handle_warn_check_window_timer_eq_without_check_hitpause(
    path, original_content, expected_content
):
    path = Path(path + ".gml")
    script = make_script(path=path, original_content=original_content)
    sut = (
        rivals_workshop_assistant.warning_handling.hitpause.CheckWindowTimerEqualsWithoutCheckHitpause()
    )

    sut.apply(script)

    assert script == make_script(
        path, original_content=original_content, working_content=expected_content
    )


@pytest.mark.parametrize(
    "path, original_content, expected_content",
    [
        pytest.param("post_draw", "nothing to do", "nothing to do"),
        pytest.param(
            "post_draw",
            f"if window_timer % 3 == 0",
            f"if window_timer % 3 == 0{rivals_workshop_assistant.warning_handling.hitpause.CheckWindowTimerModuloWithoutCheckHitpause.warning_text}",
        ),
        pytest.param(
            "post_draw",
            f"if window_timer % 3 = 0",
            f"if window_timer % 3 = 0{rivals_workshop_assistant.warning_handling.hitpause.CheckWindowTimerModuloWithoutCheckHitpause.warning_text}",
        ),
        pytest.param(
            "post_draw",
            f"if (window_timer % 3 == 0)",
            f"if (window_timer % 3 == 0){rivals_workshop_assistant.warning_handling.hitpause.CheckWindowTimerModuloWithoutCheckHitpause.warning_text}",
        ),
        pytest.param(
            "post_draw",
            f" if   (  window_timer   %    3  == 0 )",
            f" if   (  window_timer   %    3  == 0 ){rivals_workshop_assistant.warning_handling.hitpause.CheckWindowTimerModuloWithoutCheckHitpause.warning_text}",
        ),
        pytest.param(
            "post_draw",
            f"if !hitpause\nif window_timer % 3 == 0",
            f"if !hitpause\nif window_timer % 3 == 0",
        ),
    ],
)
def test_handle_warn_check_window_timer_mod_without_check_hitpause(
    path, original_content, expected_content
):
    path = Path(path + ".gml")
    script = make_script(path=path, original_content=original_content)
    sut = (
        rivals_workshop_assistant.warning_handling.hitpause.CheckWindowTimerModuloWithoutCheckHitpause()
    )

    sut.apply(script)

    assert script == make_script(
        path, original_content=original_content, working_content=expected_content
    )
