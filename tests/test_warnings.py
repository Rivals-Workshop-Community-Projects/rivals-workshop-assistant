from pathlib import Path

import pytest

import rivals_workshop_assistant.warning_handling.desync as desync
import rivals_workshop_assistant.warning_handling.hitpause as hitpause
import rivals_workshop_assistant.warning_handling.warnings as warnings
from rivals_workshop_assistant.assistant_config_mod import (
    WARNINGS_FIELD,
    WARNING_DESYNC_OBJECT_VAR_SET_IN_DRAW_SCRIPT_VALUE,
)
from rivals_workshop_assistant.warning_handling import remove_warnings, handle_warning
from tests.testing_helpers import make_script


def test_get_warning_types():
    config = {WARNINGS_FIELD: [WARNING_DESYNC_OBJECT_VAR_SET_IN_DRAW_SCRIPT_VALUE]}

    result = warnings.get_warning_types(config)

    assert result == {desync.ObjectVarSetInDrawScript()}


@pytest.mark.parametrize(
    "path, original_content, expected_content",
    [
        pytest.param("post_draw", "nothing to do", "nothing to do"),
        pytest.param(
            "post_draw",
            "global = 3",
            f"global = 3{desync.ObjectVarSetInDrawScript.get_warning_text()}",
        ),
        pytest.param(
            "post_draw",
            "okay line\nglobal = 3\nalso fine",
            f"okay line\nglobal = 3{desync.ObjectVarSetInDrawScript.get_warning_text()}\nalso fine",
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
            f"a += 3{desync.ObjectVarSetInDrawScript.get_warning_text()}",
        ),
        pytest.param(
            "post_draw",
            "a += 3   // NO-WARN",
            "a += 3   // NO-WARN",
        ),
        pytest.param(
            "css_draw",
            "global = 3",
            f"global = 3",
        ),
    ],
)
def test_handle_warn_setting_nonlocal_var_in_draw_script(
    path, original_content, expected_content
):
    path = Path(path + ".gml")
    script = make_script(path=path, original_content=original_content)
    sut = desync.ObjectVarSetInDrawScript()

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
            f"if window_timer == 3{hitpause.CheckWindowTimerEqualsWithoutCheckHitpause.get_warning_text()}",
        ),
        pytest.param(
            "post_draw",
            f"if window_timer = 3",
            f"if window_timer = 3{hitpause.CheckWindowTimerEqualsWithoutCheckHitpause.get_warning_text()}",
        ),
        pytest.param(
            "post_draw",
            f"if (window_timer == 3)",
            f"if (window_timer == 3){hitpause.CheckWindowTimerEqualsWithoutCheckHitpause.get_warning_text()}",
        ),
        pytest.param(
            "post_draw",
            f" if   (  window_timer   ==    3  )",
            f" if   (  window_timer   ==    3  ){hitpause.CheckWindowTimerEqualsWithoutCheckHitpause.get_warning_text()}",
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
    sut = hitpause.CheckWindowTimerEqualsWithoutCheckHitpause()

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
            f"if window_timer % 3 == 0{hitpause.CheckWindowTimerModuloWithoutCheckHitpause.get_warning_text()}",
        ),
        pytest.param(
            "post_draw",
            f"if window_timer % 3 = 0",
            f"if window_timer % 3 = 0{hitpause.CheckWindowTimerModuloWithoutCheckHitpause.get_warning_text()}",
        ),
        pytest.param(
            "post_draw",
            f"if (window_timer % 3 == 0)",
            f"if (window_timer % 3 == 0){hitpause.CheckWindowTimerModuloWithoutCheckHitpause.get_warning_text()}",
        ),
        pytest.param(
            "post_draw",
            f" if   (  window_timer   %    3  == 0 )",
            f" if   (  window_timer   %    3  == 0 ){hitpause.CheckWindowTimerModuloWithoutCheckHitpause.get_warning_text()}",
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
    sut = hitpause.CheckWindowTimerModuloWithoutCheckHitpause()

    sut.apply(script)

    assert script == make_script(
        path, original_content=original_content, working_content=expected_content
    )


def test__no_repeated_warning():
    original_content = f"""\
switch (lock)
{{
    default:
    case 0:
        break
    case 1:
        _offscreenx = 2;
        _offscreeny = y - view_get_yview();{desync.UnsafeCameraReadY.get_warning_text()}
        _offscreenId = 4;
    //Left
    case 2:
        break
}}
    """
    path = Path("article1_update.gml")
    script = make_script(path=path, original_content=original_content)

    handle_warning(
        assistant_config={"warnings": ["desync_unsafe_camera_read"]}, scripts=[script]
    )

    assert (
        script.working_content
        == make_script(
            path=path,
            original_content=original_content,
            working_content=original_content,
        ).working_content
    )


@pytest.mark.parametrize(
    "original, expected",
    [
        pytest.param("nothing to do", "nothing to do"),
        pytest.param(
            f"if window_timer % 3 == 0{hitpause.CheckWindowTimerModuloWithoutCheckHitpause.get_warning_text()}",
            f"if window_timer % 3 == 0\n",
        ),
        pytest.param(
            f"blah                {desync.ObjectVarSetInDrawScript.get_warning_text()}",
            f"blah                \n",
        ),
        pytest.param(
            f"twice! {desync.ObjectVarSetInDrawScript.get_warning_text()}{desync.ObjectVarSetInDrawScript.get_warning_text()}",
            f"twice! \n",
        ),
        pytest.param(
            f"""\
newline {desync.ObjectVarSetInDrawScript.get_warning_text()}
more""",
            f"""\
newline 
more""",
        ),
    ],
)
def test__remove_warnings(original, expected):
    actual = remove_warnings(original)
    assert actual == expected
