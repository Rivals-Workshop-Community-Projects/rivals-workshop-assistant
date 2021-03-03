import pytest

from rivals_workshop_assistant.injection.dependencies import Define
from rivals_workshop_assistant.injection.library import get_injection_library_from_gml


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
    library = get_injection_library_from_gml(content)

    assert library == [define]
