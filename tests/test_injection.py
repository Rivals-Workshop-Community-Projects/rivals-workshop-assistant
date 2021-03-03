from pathlib import Path

import pytest

import rivals_workshop_assistant.injection as injection


def test_define_gml():
    sut = injection.Define(name='name', version=12, docs='docs', content='gml')
    assert sut.gml == """\
#define name // Version 12
    // docs
    gml"""


def test_define_gml_multiple_lines():
    sut = injection.Define(name='name', version=12, docs='docs\ndocs', content='gml\ngml')
    assert sut.gml == """\
#define name // Version 12
    // docs
    // docs
    gml
    gml"""


def test_define_gml_parameters():
    sut = injection.Define(name='name', version=12, docs='docs', content='gml', params=['foo', 'bar'])
    assert sut.gml == """\
#define name(foo, bar) // Version 12
    // docs
    gml"""


def test_apply_injection_nothing():
    result_scripts = injection.apply_injection(scripts={}, injection_library=[])
    assert result_scripts == {}


def test_apply_injection_no_injections():
    scripts = {Path('a'): 'content'}

    result_scripts = injection.apply_injection(scripts=scripts, injection_library=[])
    assert result_scripts == scripts


def test_apply_injection_irrelevant_injection():
    scripts = {Path('a'): 'content'}
    define = injection.Define(name='', version=0, docs='', content='')

    result_scripts = injection.apply_injection(scripts=scripts, injection_library=[define])
    assert result_scripts == scripts


@pytest.mark.parametrize(
    "script, define",
    [
        pytest.param("""\
content
define1()""",
                     injection.Define(
                         name='define1', version=0, docs='docs', content='content')
                     ),
        pytest.param("""\
content
define2()""",
                     injection.Define(
                         name='define2', version=4, docs='docs2\ndocs2', content='content2\ncontent2')

                     ),
    ],
)
def test_apply_injection_makes_injection(script, define):
    scripts = {Path('a'): script}

    result_scripts = injection.apply_injection(scripts=scripts, injection_library=[define])
    assert result_scripts == {Path('a'): f"""\
{script}

// vvv LIBRARY DEFINES AND MACROS vvv
{define.gml}
// ^^^ END: LIBRARY DEFINES AND MACROS ^^^"""}
