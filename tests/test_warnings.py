from pathlib import Path

import pytest

from tests.testing_helpers import make_script
import rivals_workshop_assistant.warning_handling as src


@pytest.mark.parametrize(
    "path, original_content, expected_content",
    [
        pytest.param("post_draw", "nothing to do", "nothing to do"),
        pytest.param(
            "post_draw",
            "global = 3",
            f"global = 3{src.PossibleDesyncWarning.warning_text}",
        ),
        pytest.param(
            "post_draw",
            "okay line\nglobal = 3\nalso fine",
            f"okay line\nglobal = 3{src.PossibleDesyncWarning.warning_text}\nalso fine",
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
            f"a += 3{src.PossibleDesyncWarning.warning_text}",
        ),
    ],
)
def test_handle_warn_setting_nonlocal_var_in_draw_script(
    path, original_content, expected_content
):
    path = Path(path + ".gml")
    script = make_script(path=path, original_content=original_content)
    sut = src.PossibleDesyncWarning()

    sut.apply(script)

    assert script == make_script(
        path, original_content=original_content, working_content=expected_content
    )
