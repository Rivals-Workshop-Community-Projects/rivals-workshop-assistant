from copy import deepcopy
from pathlib import Path

import pytest

from rivals_workshop_assistant import code_generation as src
from tests.testing_helpers import make_script, make_time, TEST_LATER_DATETIME_STRING

PATH_A = Path("a")


@pytest.mark.parametrize(
    "original_content, expected_content",
    [
        pytest.param("nothing to do", "nothing to do"),
        pytest.param("before$foreach things", "before$foreach things"),
        pytest.param("foreach things$", "foreach things$"),
        pytest.param("a//$foreach things$b", "a//$foreach things$b"),
        pytest.param(
            "$foreach alist$",
            """\
for (var alist_item_i=0; alist_item_i<array_length(alist); alist_item_i++) {
    var alist_item = alist[alist_item_i]
}""",
        ),
        pytest.param(
            "$foreach blah$",
            """\
for (var blah_item_i=0; blah_item_i<array_length(blah); blah_item_i++) {
    var blah_item = blah[blah_item_i]
}""",
        ),
        pytest.param(
            "    $foreach blah$",
            """\
    for (var blah_item_i=0; blah_item_i<array_length(blah); blah_item_i++) {
        var blah_item = blah[blah_item_i]
    }""",
        ),
        pytest.param(
            "  a  $foreach blah$",
            """\
  a  for (var blah_item_i=0; blah_item_i<array_length(blah); blah_item_i++) {
    var blah_item = blah[blah_item_i]
}""",
        ),
        pytest.param(
            "$foreach things$",
            """\
for (var thing_i=0; thing_i<array_length(things); thing_i++) {
    var thing = things[thing_i]
}""",
        ),
    ],
)
def test_handle_codegen__for_loop(original_content, expected_content):
    scripts = [make_script(PATH_A, original_content=original_content)]

    src.handle_codegen(scripts)

    assert scripts == [
        make_script(
            PATH_A, original_content=original_content, working_content=expected_content
        )
    ]


def test_already_processed_file__nothing_happens():
    original_content = "$foreach blah$"
    orig_scripts = [
        make_script(
            PATH_A,
            original_content=original_content,
            processed_time=make_time(TEST_LATER_DATETIME_STRING),
        )
    ]
    scripts = deepcopy(orig_scripts)

    src.handle_codegen(scripts)

    assert scripts == orig_scripts
