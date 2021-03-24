from pathlib import Path

import pytest

import rivals_workshop_assistant.injection.application as application
from rivals_workshop_assistant.injection.dependency_handling import Define, \
    Macro

PATH_A = Path('a')


def test_apply_injection_no_injections():
    scripts = {PATH_A: 'content'}

    result_scripts = application.apply_injection(scripts=scripts,
                                                 injection_library=[])
    assert result_scripts == scripts


def test_apply_injection_irrelevant_injection():
    scripts = {PATH_A: 'content'}
    define = Define(name='', version=0, docs='', content='')

    result_scripts = application.apply_injection(scripts=scripts,
                                                 injection_library=[define])
    assert result_scripts == scripts


define1 = Define(
    name='define1', version=0, docs='docs', content='content')
define2 = Define(
    name='define2', version=4, docs='docs2\ndocs2',
    content='content2\ncontent2')


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

    result_scripts = application.apply_injection(scripts=scripts,
                                                 injection_library=[define])
    assert result_scripts == {PATH_A: f"""\
{script}

{application.INJECTION_START_HEADER}
{define.gml}
{application.INJECTION_END_HEADER}"""}


def test_apply_injection_make_multiple_injections():
    script = """\
content
define1()
content
define2()
content"""
    scripts = {PATH_A: script}
    library = [define1, define2]

    result_scripts = application.apply_injection(scripts=scripts,
                                                 injection_library=library)
    assert result_scripts == {PATH_A: f"""\
{script}

{application.INJECTION_START_HEADER}
{define1.gml}

{define2.gml}
{application.INJECTION_END_HEADER}"""}


def test_replace_existing_library_dependencies():
    script_content = 'define1()'

    script = f"""\
{script_content}
{application.INJECTION_START_HEADER}
{define2.gml}
{application.INJECTION_END_HEADER}
"""
    scripts = {PATH_A: script}
    library = [define1]

    result_scripts = application.apply_injection(scripts=scripts,
                                                 injection_library=library)
    assert result_scripts == {PATH_A: f"""\
{script_content}

{application.INJECTION_START_HEADER}
{define1.gml}
{application.INJECTION_END_HEADER}"""}


def test_removes_injection_when_not_needed():
    script_content = 'content'
    script = f"""\
{script_content}

{application.INJECTION_START_MARKER}

{define1.gml}


{application.INJECTION_END_HEADER}"""

    scripts = {PATH_A: script}
    result_scripts = application.apply_injection(scripts, [])
    assert result_scripts == {PATH_A: script_content}


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

    scripts = {PATH_A: script}
    result_scripts = application.apply_injection(scripts, [define1])
    assert result_scripts == scripts


def test_recursive_dependencies():
    script = f"""\
define_recursive()"""

    scripts = {PATH_A: script}
    recursive_define = Define(
        name='define_recursive', version=0, docs='recursive_docs',
        content='define1()')
    library = [recursive_define, define1]

    result_scripts = application.apply_injection(scripts, library)
    assert result_scripts == {PATH_A: f"""\
{script}

{application.INJECTION_START_HEADER}
{recursive_define.gml}

{define1.gml}
{application.INJECTION_END_HEADER}"""}


def test_macro():
    script = f"""\
some_macro

blah"""

    scripts = {PATH_A: script}
    some_macro = Macro(name='some_macro', value='value')
    library = [some_macro]

    result_scripts = application.apply_injection(scripts, library)
    assert result_scripts == {PATH_A: f"""\
{script}

{application.INJECTION_START_HEADER}
{some_macro.gml}
{application.INJECTION_END_HEADER}"""}


def test_doesnt_provide_user_supplied_define():
    script = f"""\
my_define()

#define my_define 
    my define content

"""

    scripts = {PATH_A: script}
    my_define_library_version = Define(name='my_define',
                                       content='library version')
    library = [my_define_library_version]

    result_scripts = application.apply_injection(scripts, library)
    assert result_scripts == {PATH_A: script.rstrip()}


def test_does_provide_assistant_supplied_define():
    script = f"""\
define1()

{application.INJECTION_START_HEADER}
{define1.gml}
{application.INJECTION_END_HEADER}"""
    scripts = {PATH_A: script}

    library = [define1]
    result_scripts = application.apply_injection(scripts, library)
    assert result_scripts == scripts


def test_doesnt_provide_user_supplied_macro():
    script = f"""\
print(my_macro)

#macro my_macro 2"""

    scripts = {PATH_A: script}
    my_macro_library_version = Macro(name='my_macro', value='3')
    library = [my_macro_library_version]

    result_scripts = application.apply_injection(scripts, library)
    assert result_scripts == {PATH_A: script.rstrip()}
