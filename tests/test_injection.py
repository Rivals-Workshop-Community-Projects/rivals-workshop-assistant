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


PATH_A = Path('a')


def test_apply_injection_no_injections():
    scripts = {PATH_A: 'content'}

    result_scripts = injection.apply_injection(scripts=scripts, injection_library=[])
    assert result_scripts == scripts


def test_apply_injection_irrelevant_injection():
    scripts = {PATH_A: 'content'}
    define = injection.Define(name='', version=0, docs='', content='')

    result_scripts = injection.apply_injection(scripts=scripts, injection_library=[define])
    assert result_scripts == scripts


define1 = injection.Define(
    name='define1', version=0, docs='docs', content='content')
define2 = injection.Define(
    name='define2', version=4, docs='docs2\ndocs2', content='content2\ncontent2')


@pytest.mark.parametrize(
    "script, define",
    [
        pytest.param("""\
content
define1()""",
                     define1),
        pytest.param("""\
content
define2()""",
                     define2),
    ],
)
def test_apply_injection_makes_injection(script, define):
    scripts = {PATH_A: script}

    result_scripts = injection.apply_injection(scripts=scripts, injection_library=[define])
    assert result_scripts == {PATH_A: f"""\
{script}

{injection.INJECTION_START_HEADER}
{define.gml}
{injection.INJECTION_END_HEADER}"""}


def test_apply_injection_make_multiple_injections():
    script = """\
content
define1()
content
define2()
content"""
    scripts = {PATH_A: script}
    library = [define1, define2]

    result_scripts = injection.apply_injection(scripts=scripts, injection_library=library)
    assert result_scripts == {PATH_A: f"""\
{script}

{injection.INJECTION_START_HEADER}
{define1.gml}

{define2.gml}
{injection.INJECTION_END_HEADER}"""}


def test_replace_existing_library_dependencies():
    script_content = 'define1()'

    script = f"""\
{script_content}
{injection.INJECTION_START_HEADER}
{define2.gml}
{injection.INJECTION_END_HEADER}
"""
    scripts = {PATH_A: script}
    library = [define1]

    result_scripts = injection.apply_injection(scripts=scripts, injection_library=library)
    assert result_scripts == {PATH_A: f"""\
{script_content}

{injection.INJECTION_START_HEADER}
{define1.gml}
{injection.INJECTION_END_HEADER}"""}


def test_removes_injection_when_not_needed():
    script_content = 'content'
    script = f"""\
{script_content}

{injection.INJECTION_START_MARKER}

{define1.gml}


{injection.INJECTION_END_HEADER}"""

    scripts = {PATH_A: script}
    result_scripts = injection.apply_injection(scripts, [])
    assert result_scripts == {PATH_A: script_content}


def test_toggled_off_makes_changes():
    script_content = f"""\
content
define1()
// NO-INJECT"""

    script = f"""\
{script_content}
{injection.INJECTION_START_HEADER}
{define2.gml}
{injection.INJECTION_END_HEADER}
"""

    scripts = {PATH_A: script}
    result_scripts = injection.apply_injection(scripts, [define1])
    assert result_scripts == scripts
