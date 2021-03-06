from pathlib import Path
from dataclasses import dataclass

from testfixtures import TempDirectory

from rivals_workshop_assistant.injection import apply_injection
from rivals_workshop_assistant.injection.library import INJECT_FOLDER
from rivals_workshop_assistant.injection.dependency_handling import Define
from rivals_workshop_assistant.main import read_scripts
from rivals_workshop_assistant import injection


@dataclass
class ScriptWithPath:
    path: Path
    content: str

    def absolute_path(self, tmp: TempDirectory):
        return Path(tmp.path) / self.path


script_1 = ScriptWithPath(
    path=Path('scripts/script_1.gml'),
    content="""\
script 1
    content
    needs_other()
    
    
    another_func()"""
)

script_subfolder = ScriptWithPath(
    path=Path('scripts/subfolder/script_subfolder.gml'),
    content="""\
script in subfolder
func()"""
)

injection_at_root = ScriptWithPath(
    path=INJECT_FOLDER / Path('at_root.gml'),
    content="""\
#define func {
    // some docs
    //some more docs
    func content

}

#define another_func
    another func 
    content

""")

injection_in_subfolder = ScriptWithPath(
    path=INJECT_FOLDER / Path('subfolder/in_subfolder.gml'),
    content="""\
#define needs_other {
    other()
}

#define other
    other content

"""
)

func = Define(name='func', docs='some docs\nsome more docs',
              content='func content')
another_func = Define(name='another_func', content='another func\ncontent')
needs_other = Define(name='needs_other', content='other()')
other = Define(name='other', content='other content')


def make_script(tmp: TempDirectory, script_with_path: ScriptWithPath):
    tmp.write(script_with_path.path.as_posix(),
              script_with_path.content.encode())


def test_read_scripts():
    with TempDirectory() as tmp:
        make_script(tmp, script_1)
        make_script(tmp, script_subfolder)

        result = read_scripts(Path(tmp.path))
        assert result == {
            script_1.absolute_path(tmp): script_1.content,
            script_subfolder.absolute_path(tmp): script_subfolder.content
        }


def test_read_injection_library():
    with TempDirectory() as tmp:
        make_script(tmp, injection_at_root)
        make_script(tmp, injection_in_subfolder)

        result_library = injection.read_injection_library(Path(tmp.path))
        assert result_library == [func, another_func, needs_other, other]


def test_full_injection():
    with TempDirectory() as tmp:
        make_script(tmp, script_1)
        make_script(tmp, script_subfolder)
        make_script(tmp, injection_at_root)
        make_script(tmp, injection_in_subfolder)

        scripts = read_scripts(Path(tmp.path))
        library = injection.read_injection_library(Path(tmp.path))
        result_scripts = apply_injection(scripts=scripts,
                                         injection_library=library)

        assert result_scripts == {
            script_1.absolute_path(tmp): f"""\
{script_1.content}

{injection.application.INJECTION_START_HEADER}
{another_func.gml}

{needs_other.gml}

{other.gml}
{injection.application.INJECTION_END_HEADER}""",
            script_subfolder.absolute_path(tmp): f"""\
{script_subfolder.content}

{injection.application.INJECTION_START_HEADER}
{func.gml}
{injection.application.INJECTION_END_HEADER}"""}
