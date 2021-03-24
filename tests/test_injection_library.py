import pytest

from rivals_workshop_assistant.injection.dependency_handling import Define, \
    Macro
from rivals_workshop_assistant.injection.library import \
    get_injection_library_from_gml


def test_empty():
    library = get_injection_library_from_gml('')
    assert library == []


def test_no_dependencies():
    library = get_injection_library_from_gml('nothing helpful here')
    assert library == []


@pytest.mark.parametrize(
    "content, define",
    [
        pytest.param("""\
#define name
    content""",
                     Define(name='name', content='content')),
        pytest.param("""\
content
#define other
    different content
""",
                     Define(name='other', content='different content')),
    ],
)
def test_loads_dependency_minimal(content, define):
    actual_library = get_injection_library_from_gml(content)

    assert actual_library == [define]


@pytest.mark.parametrize(
    "content, library",
    [
        pytest.param("""\
#define define1
    content1
    
#define define2
    content2
    more content2        
""",
                     [
                         Define(name='define1', content='content1'),
                         Define(name='define2',
                                content='content2\nmore content2')
                     ]),
    ]
)
def test_loads_multiple_dependencies_minimal(content, library):
    actual_library = get_injection_library_from_gml(content)

    assert actual_library == library


@pytest.mark.parametrize(
    "content, define",
    [
        pytest.param("""\
#define name {
    content}""",
                     Define(name='name', content='content')),
        pytest.param("""\
content
#define other{
    different content

}
""",
                     Define(name='other', content='different content')),
        pytest.param("""\
#define func {
    // some docs
    //some more docs
    func content

}
""",
                     Define(name='func', docs='some docs\nsome more docs',
                            content='func content')),
    ],
)
def test_loads_dependency_braces(content, define):
    actual_library = get_injection_library_from_gml(content)

    assert actual_library == [define]


@pytest.mark.parametrize(
    "content",
    [
        pytest.param("""\
#define name {
    content"""),
        pytest.param("""\
content
#define other
    different content

}
"""),
        pytest.param("""\
content
#define other {
    if {
    }
"""),
    ],
)
def test_loads_dependency_mismatched_braces(content):
    with pytest.raises(ValueError):
        get_injection_library_from_gml(content)


def test_loads_dependency_matched_braces_that_look_mismatched():
    actual_library = get_injection_library_from_gml("""\
#define define1
    blah
    if thing {
    } 
""")
    assert actual_library == [
        Define(name='define1', content='blah\nif thing {\n}')
    ]


@pytest.mark.parametrize(
    "content, define",
    [
        pytest.param("""\
#define name 
    //plenty
    //of
    //docs 
    content""",
                     Define(name='name', docs='plenty\nof\ndocs',
                            content='content')),
        pytest.param("""\
content
#define other
//some docs
    different content

""",
                     Define(name='other', docs='some docs',
                            content='different content')),
    ],
)
def test_loads_dependency_gets_docs(content, define):
    actual_library = get_injection_library_from_gml(content)

    assert actual_library[0].docs == define.docs


@pytest.mark.parametrize(
    "content, define",
    [
        pytest.param("""\
#define name
some
content""",
                     Define(name='name', content='some\ncontent')),
        pytest.param("""\
content
#define other
                different
                content
""",
                     Define(name='other', content='different\ncontent')),
        pytest.param("""\
content
#define hard
    several
    different   
        indentations
    to
handle
""",
                     Define(name='hard',
                            content='    several\n    different\n        indentations\n    to\nhandle')),
    ],
)
def test_loads_dependency_weird_indentation(content, define):
    actual_library = get_injection_library_from_gml(content)

    assert actual_library == [define]


@pytest.mark.parametrize(
    "content, library",
    [
        pytest.param("""\
#define define1
    content1
    
#macro multi some
    content       
""",
                     [
                         Define(name='define1', content='content1'),
                         Macro(name='multi', value='some\n    content')
                     ]),
    ]
)
def test_loads_with_macro(content, library):
    actual_library = get_injection_library_from_gml(content)

    assert actual_library == library
