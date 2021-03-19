from dataclasses import dataclass
from pathlib import Path

from testfixtures import TempDirectory

from rivals_workshop_assistant.injection import installation as src


@dataclass
class ScriptWithPath:
    path: Path
    content: str

    def absolute_path(self, tmp: TempDirectory):
        return Path(tmp.path) / self.path


def make_script(tmp: TempDirectory, script_with_path: ScriptWithPath):
    tmp.write(script_with_path.path.as_posix(),
              script_with_path.content.encode())


def make_version(version_str: str) -> src.Version:
    major, minor, patch = (int(char) for char in version_str.split('.'))
    return src.Version(major=major, minor=minor, patch=patch)


def make_release(version_str: str, url: str) -> src.Release:
    version = make_version(version_str)
    return src.Release(version=version, download_url=url)


test_date_string = '2019-12-04'


def assert_script(tmp, script: ScriptWithPath):
    actual_content = tmp.read(filepath=script.path.as_posix(),
                              encoding='utf8')
    assert actual_content == script.content
