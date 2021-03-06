from pathlib import Path
from dataclasses import dataclass

from testfixtures import TempDirectory

from rivals_workshop_assistant.main import read_scripts


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
    content"""
)

script_subfolder = ScriptWithPath(
    path=Path('scripts/subfolder/script_subfolder.gml'),
    content="""\
script in subfolder"""
)


def make_script(tmp: TempDirectory, script_with_path: ScriptWithPath):
    tmp.write(script_with_path.path.as_posix(), script_with_path.content.encode())


def test_read_scripts():
    with TempDirectory() as tmp:

        make_script(tmp, script_1)
        make_script(tmp, script_subfolder)

        result = read_scripts(Path(tmp.path))
        assert result == {
            script_1.absolute_path(tmp): script_1.content,
            script_subfolder.absolute_path(tmp): script_subfolder.content
        }
