from copy import deepcopy
from pathlib import Path

import pytest

import rivals_workshop_assistant.script_handling.injection.application as application
from rivals_workshop_assistant.aseprite_handling import Window
from rivals_workshop_assistant.script_handling.injection.dependency_handling import (
    Define,
    Macro,
)
from tests.test_aseprite_handling import make_anim
from tests.testing_helpers import (
    make_script,
    make_time,
    TEST_LATER_DATETIME_STRING,
    PATH_A,
)
from loguru import logger

logger.remove()


def test_apply_injection_no_injections():
    orig_scripts = [make_script(PATH_A, "content")]
    scripts = deepcopy(orig_scripts)

    application.apply_injection(scripts=scripts, injection_library=[], anims=[])
    assert scripts == orig_scripts


def test_apply_injection_irrelevant_injection():
    orig_scripts = [make_script(PATH_A, "content")]
    scripts = deepcopy(orig_scripts)
    define = Define(name="irrelevant", version=0, docs="", content="")

    application.apply_injection(scripts=scripts, injection_library=[define], anims=[])
    assert orig_scripts == scripts


define1 = Define(
    name="define1", params=["param"], version=0, docs="docs", content="content"
)
define2 = Define(
    name="define2", version=4, docs="docs2\ndocs2", content="content2\ncontent2"
)


@pytest.mark.parametrize(
    "script, define",
    [
        pytest.param(
            """\
content
define1()""",
            define1,
        ),
        pytest.param(
            """\
content
define2()""",
            define2,
        ),
    ],
)
def test_apply_injection_makes_injection(script, define):
    scripts = [make_script(PATH_A, script)]

    application.apply_injection(scripts=scripts, injection_library=[define], anims=[])
    assert scripts == [
        make_script(
            PATH_A,
            original_content=script,
            working_content=f"""\
{script}

{application.INJECTION_START_HEADER}
{define.gml}
{application.INJECTION_END_HEADER}""",
        )
    ]


def test_apply_injection_make_multiple_injections():
    script = """\
content
define1()
content
define2()
content"""
    scripts = [make_script(PATH_A, script)]
    library = [define1, define2]

    application.apply_injection(scripts=scripts, injection_library=library, anims=[])
    assert scripts == [
        make_script(
            PATH_A,
            original_content=script,
            working_content=f"""\
{script}

{application.INJECTION_START_HEADER}
{define1.gml}

{define2.gml}
{application.INJECTION_END_HEADER}""",
        )
    ]


@pytest.mark.parametrize(
    "header",
    [
        pytest.param(application.INJECTION_START_HEADER),
        pytest.param(application.OLD_INJECTION_START_HEADERS[0]),
    ],
)
def test_replace_existing_library_dependencies(header):
    script_content = "define1()"

    script = f"""\
{script_content}
{header}
{define1.gml}
{define2.gml}
{application.INJECTION_END_HEADER}
"""

    actual_scripts = [make_script(PATH_A, script)]
    library = [define1]
    application.apply_injection(
        scripts=actual_scripts, injection_library=library, anims=[]
    )

    expected_scripts = [
        make_script(
            PATH_A,
            original_content=script,
            working_content=f"""\
{script_content}

{application.INJECTION_START_HEADER}
{define1.gml}
{application.INJECTION_END_HEADER}""",
        )
    ]
    assert expected_scripts == actual_scripts


def test_removes_injection_when_not_needed():
    script_content = "content"
    script = f"""\
{script_content}

{application.INJECTION_START_MARKER}

{define1.gml}


{application.INJECTION_END_HEADER}"""

    scripts = [make_script(PATH_A, script)]
    application.apply_injection(scripts=scripts, injection_library=[define1], anims=[])
    assert scripts == [
        make_script(PATH_A, original_content=script, working_content=script_content)
    ]


def test_toggled_off_makes_changes():
    script_content = f"""\
content
define1()
// NO-INJECT"""

    script = f"""\
{script_content}
{application.INJECTION_START_HEADER}
{define2.gml}
{application.INJECTION_END_HEADER}
"""
    orig_scripts = [make_script(PATH_A, script)]
    scripts = deepcopy(orig_scripts)

    application.apply_injection(scripts, [define1], anims=[])
    assert scripts == orig_scripts


def test_recursive_dependencies():
    script = f"""\
define_recursive()"""

    scripts = [make_script(PATH_A, script)]
    recursive_define = Define(
        name="define_recursive", version=0, docs="recursive_docs", content="define1()"
    )
    library = [recursive_define, define1]

    application.apply_injection(scripts, library, anims=[])

    assert scripts == [
        make_script(
            PATH_A,
            original_content=script,
            working_content=f"""\
{script}

{application.INJECTION_START_HEADER}
{recursive_define.gml}

{define1.gml}
{application.INJECTION_END_HEADER}""",
        )
    ]


def test_macro():
    script = f"""\
some_macro

blah"""

    scripts = [make_script(PATH_A, script)]
    some_macro = Macro(name="some_macro", value="value")
    library = [some_macro]

    application.apply_injection(scripts, library, anims=[])
    assert scripts == [
        make_script(
            PATH_A,
            original_content=script,
            working_content=f"""\
{script}

{application.INJECTION_START_HEADER}
{some_macro.gml}
{application.INJECTION_END_HEADER}""",
        )
    ]


def test_doesnt_provide_user_supplied_define():
    script = f"""\
my_define()

#define my_define 
    my define content

"""

    scripts = [make_script(PATH_A, script)]
    my_define_library_version = Define(name="my_define", content="library version")
    library = [my_define_library_version]

    application.apply_injection(scripts, library, anims=[])
    assert scripts == [
        make_script(PATH_A, original_content=script, working_content=script.rstrip())
    ]


def test_does_provide_assistant_supplied_define():
    script = f"""\
define1()

{application.INJECTION_START_HEADER}
{define1.gml}
{application.INJECTION_END_HEADER}"""
    orig_scripts = [make_script(PATH_A, script)]
    scripts = deepcopy(orig_scripts)

    library = [define1]
    application.apply_injection(scripts, library, anims=[])
    assert scripts == orig_scripts


def test_doesnt_provide_user_supplied_macro():
    script = f"""\
print(my_macro)

#macro my_macro 2"""

    scripts = [make_script(PATH_A, script)]
    my_macro_library_version = Macro(name="my_macro", value="3")
    library = [my_macro_library_version]

    application.apply_injection(scripts, library, anims=[])
    assert scripts == [
        make_script(PATH_A, original_content=script, working_content=script.rstrip())
    ]


def test_already_processed_file__nothing_happens():
    script = """\
content
define1()"""
    define = define1

    orig_scripts = [
        make_script(
            PATH_A, script, processed_time=make_time(TEST_LATER_DATETIME_STRING)
        )
    ]
    scripts = deepcopy(orig_scripts)

    application.apply_injection(scripts=scripts, injection_library=[define], anims=[])
    assert scripts == orig_scripts


def test_get_anim_data_gmls_needed_in_gml():
    path = Path("scripts/attacks/dattack.gml")
    orig_content = "content"
    script = make_script(path=path, original_content=orig_content)
    scripts = [script]

    anim = make_anim(name="dattack", start=0, end=4)
    anim.windows = [Window("window", 2, 3)]
    anims = [anim]

    application.apply_injection(scripts=scripts, injection_library=[], anims=anims)

    assert scripts == [
        make_script(
            path=path,
            original_content=orig_content,
            working_content=f"""\
{orig_content}

{application.INJECTION_START_HEADER}
{anim.windows[0].gml}
{application.INJECTION_END_HEADER}""",
        )
    ]
