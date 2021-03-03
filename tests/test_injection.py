import textwrap

import rivals_workshop_assistant.injection as injection


def test_define_gml():
    sut = injection.Define(name='name', version=12, docs='docs', content='gml')
    assert sut.gml == textwrap.dedent("""\
    #define name // Version 12
        // docs
        gml""")


def test_define_gml_multiple_lines():
    sut = injection.Define(name='name', version=12, docs='docs\ndocs', content='gml\ngml')
    assert sut.gml == textwrap.dedent("""\
    #define name // Version 12
        // docs
        // docs
        gml
        gml""")


def test_define_gml_parameters():
    sut = injection.Define(name='name', version=12, docs='docs', content='gml', params=['foo', 'bar'])
    assert sut.gml == textwrap.dedent("""\
    #define name(foo, bar) // Version 12
        // docs
        gml""")
