from copy import deepcopy

import pytest

import rivals_workshop_assistant.script_handling.injection.application as application
from rivals_workshop_assistant.script_handling.injection.dependency_handling import (
    Define,
    Macro,
)
from loguru import logger

logger.remove()


def test_define_gml():
    sut = Define(name="name", version=12, docs="docs", content="gml")
    assert (
        sut.gml
        == """\
#define name // Version 12
    // docs
    gml"""
    )


def test_define_gml_multiple_lines():
    sut = Define(name="name", version=12, docs="docs\ndocs", content="gml\ngml")
    assert (
        sut.gml
        == """\
#define name // Version 12
    // docs
    // docs
    gml
    gml"""
    )


def test_define_gml_parameters():
    sut = Define(
        name="name", version=12, docs="docs", content="gml", params=["foo", "bar"]
    )
    assert (
        sut.gml
        == """\
#define name(foo, bar) // Version 12
    // docs
    gml"""
    )


def test_apply_injection_nothing():
    orig_scripts = []
    scripts = deepcopy(orig_scripts)
    application.apply_injection(scripts=scripts, injection_library=[], anims=[])
    assert scripts == orig_scripts


def test_define_no_docs():
    sut = Define(name="name", version=12, content="gml", params=["foo", "bar"])
    assert (
        sut.gml
        == """\
#define name(foo, bar) // Version 12
    gml"""
    )


def test_macro():
    sut = Macro(name="name", value="gml")
    assert (
        sut.gml
        == """\
#macro name gml"""
    )


def test_macro_multiline():
    sut = Macro(
        name="multi",
        value="""\
line
    indented
more""",
    )
    assert (
        sut.gml
        == """\
#macro multi line
    indented
more"""
    )


@pytest.mark.parametrize(
    "content, expected",
    [
        (
            """\
blah
thing()

#define thing(){
}
""",
            True,
        ),
        (
            """\
blah

#define thing(){
}
""",
            False,
        ),
        (
            """\
blah

""",
            False,
        ),
        (
            """\
anotherthing()

#define thing(){
}
""",
            False,
        ),
        (
            """thing()

#define thing(){
}
""",
            True,
        ),
        (
            """\
#define needs_thing // Version 0
    thing()""",
            True,
        ),
        (
            """\
#define another_thing // Version 0
    another thing
    content""",
            False,
        ),
    ],
)
def test_define_is_used(content, expected):
    sut = Define(name="thing", version=0, content="blah")
    assert sut.is_used(content) == expected


@pytest.mark.parametrize(
    "content, expected",
    [
        (
            """\
blah = mymacros
#macro mymacro 4
""",
            False,
        ),
        (
            """\
mymacro;
""",
            True,
        ),
        (
            """\
    mymacro,
    """,
            True,
        ),
        (
            """\
        mymacro)
        """,
            True,
        ),
        (
            """\
        mymacro+
        """,
            True,
        ),
        (
            """\
        mymacro-
        """,
            True,
        ),
        (
            """\
        mymacro/
        """,
            True,
        ),
        (
            """\
        mymacro*
        """,
            True,
        ),
        (
            """\
        mymacro_
        """,
            False,
        ),
        (
            """\
            +mymacro
            """,
            True,
        ),
    ],
)
def test_macro_is_used(content, expected):
    sut = Macro(name="mymacro", value="blah")
    assert sut.is_used(content) == expected
