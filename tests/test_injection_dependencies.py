import rivals_workshop_assistant.injection.application as application
from rivals_workshop_assistant.injection.dependency_handling import Define, \
    Macro


def test_define_gml():
    sut = Define(name='name', version=12, docs='docs', content='gml')
    assert sut.gml == """\
#define name // Version 12
    // docs
    gml"""


def test_define_gml_multiple_lines():
    sut = Define(name='name', version=12, docs='docs\ndocs', content='gml\ngml')
    assert sut.gml == """\
#define name // Version 12
    // docs
    // docs
    gml
    gml"""


def test_define_gml_parameters():
    sut = Define(name='name', version=12, docs='docs', content='gml',
                 params=['foo', 'bar'])
    assert sut.gml == """\
#define name(foo, bar) // Version 12
    // docs
    gml"""


def test_apply_injection_nothing():
    result_scripts = application.apply_injection(scripts={},
                                                 injection_library=[])
    assert result_scripts == {}


def test_define_no_docs():
    sut = Define(name='name', version=12, content='gml', params=['foo', 'bar'])
    assert sut.gml == """\
#define name(foo, bar) // Version 12
    gml"""


def test_macro():
    sut = Macro(name='name', value='gml')
    assert sut.gml == """\
#macro name gml"""


def test_macro_multiline():
    sut = Macro(name='multi', value="""\
line
    indented
more""")
    assert sut.gml == """\
#macro multi line
    indented
more"""
