import datetime
import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops
from testfixtures import TempDirectory

from rivals_workshop_assistant.injection import installation as src
from rivals_workshop_assistant.script_mod import Script, Anim


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

TEST_ANIM_NAME = Path("testsprite.aseprite")


def make_time(time_str=TEST_DATETIME_STRING):
    return datetime.datetime.fromisoformat(time_str)


def make_anim(path: Path, modified_time=make_time(), processed_time=None):
    return Anim(path=path, modified_time=modified_time, processed_time=processed_time)


def supply_anim(
    tmp, name=TEST_ANIM_NAME, modified_time=make_time(), processed_time=None
):
    dest = Path(tmp.path) / "anims/"
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy(Path("assets" / name), dest)
    return make_anim(
        path=dest / name, modified_time=modified_time, processed_time=processed_time
    )


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
    path: Path,
    original_content: str,
    working_content: str = None,
    modified_time=make_time(),
    processed_time=None,
) -> Script:
    if working_content is None:
        working_content = original_content
    return Script(
        path=path,
        modified_time=modified_time,
        original_content=original_content,
        working_content=working_content,
        processed_time=processed_time,
    )


def make_script_from_script_with_path(tmp, script_with_path: ScriptWithPath) -> Script:
    return make_script(
        path=script_with_path.absolute_path(tmp),
        original_content=script_with_path.content,
    )
