import datetime
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops
from testfixtures import TempDirectory

from rivals_workshop_assistant.injection import installation as src
from rivals_workshop_assistant.script_mod import Script


@dataclass
class ScriptWithPath:
    path: Path
    content: str

    def absolute_path(self, tmp: TempDirectory):
        return Path(tmp.path) / self.path


def create_script(tmp: TempDirectory, script_with_path: ScriptWithPath):
    tmp.write(script_with_path.path.as_posix(), script_with_path.content.encode())


def make_version(version_str: str) -> src.Version:
    major, minor, patch = (int(char) for char in version_str.split("."))
    return src.Version(major=major, minor=minor, patch=patch)


def make_release(version_str: str, url: str) -> src.Release:
    version = make_version(version_str)
    return src.Release(version=version, download_url=url)


TEST_DATE_STRING = "2019-12-04"
ROOT_PATH = Path("C:/a/file/path/the_root/")
PATH_ABSOLUTE = Path("C:/a/file/path/the_root/scripts/script_1.gml")
PATH_RELATIVE = Path("scripts/script_1.gml")
TEST_DATETIME_STRING = "2019-12-04*09:34:22"
TEST_LATER_DATETIME_STRING = "2019-12-05*10:31:20"


def make_time(time_str=TEST_DATETIME_STRING):
    return datetime.datetime.fromisoformat(time_str)


def assert_script_with_path(tmp, script: ScriptWithPath):
    actual_content = tmp.read(filepath=script.path.as_posix(), encoding="utf8")
    assert actual_content == script.content


def make_canvas(width, height):
    return Image.new("RGBA", (width, height))


def assert_images_equal(img1, img2):
    img1 = img1.convert("RGB")
    img2 = img2.convert("RGB")
    assert not ImageChops.difference(img1, img2).getbbox()


def make_script(
    path: Path, original_content: str, working_content: str = None
) -> Script:
    if working_content is None:
        working_content = original_content
    return Script(
        path=path,
        modified_time=make_time(),
        original_content=original_content,
        working_content=working_content,
    )


def make_script_from_script_with_path(tmp, script_with_path: ScriptWithPath) -> Script:
    return make_script(
        path=script_with_path.absolute_path(tmp),
        original_content=script_with_path.content,
    )
