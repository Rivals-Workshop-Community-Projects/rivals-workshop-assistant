from rivals_workshop_assistant.injection.dependencies import Define
from rivals_workshop_assistant.injection.library import get_injection_library_from_gml


def test_empty():
    library = get_injection_library_from_gml('')
    assert library == []

def test_no_dependencies():
    library = get_injection_library_from_gml('nothing helpful here')
    assert library == []

# def test_loads_dependency_minimal():
#     library = get_injection_library_from_gml("""\
# #define name
#     content""")
#
#     assert library == [Define(name='name', version=0, content='content')]