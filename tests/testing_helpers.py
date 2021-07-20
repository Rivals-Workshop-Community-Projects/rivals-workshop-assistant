import configparser
import datetime
import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops
from testfixtures import TempDirectory

import rivals_workshop_assistant.updating
from rivals_workshop_assistant import assistant_config_mod
from rivals_workshop_assistant.script_mod import Script
from rivals_workshop_assistant.aseprite_handling import Aseprite

PATH_A = Path("a")


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: integration tests")
    config.addinivalue_line(
        "markers",
        "aseprite: require a path to a working aseprite.exe in dev_config.ini",
    )


@dataclass
class ScriptWithPath:
    path: Path
    content: str

    def absolute_path(self, tmp: TempDirectory):
        return Path(tmp.path) / self.path


def create_script(tmp: TempDirectory, script_with_path: ScriptWithPath):
    tmp.write(script_with_path.path.as_posix(), script_with_path.content.encode())


def make_version(version_str: str) -> rivals_workshop_assistant.updating.Version:
    major, minor, patch = (int(char) for char in version_str.split("."))
    return rivals_workshop_assistant.updating.Version(
        major=major, minor=minor, patch=patch
    )


def make_release(
    version_str: str, url: str
) -> rivals_workshop_assistant.updating.Release:
    version = make_version(version_str)
    return rivals_workshop_assistant.updating.Release(
        version=version, download_url=url, release_dict={}
    )


TEST_DATE_STRING = "2019-12-04"
ROOT_PATH = Path("C:/a/file/path/the_root/")
PATH_ABSOLUTE = Path("C:/a/file/path/the_root/scripts/script_1.gml")
PATH_RELATIVE = Path("scripts/script_1.gml")
TEST_DATETIME_STRING = "2019-12-04*09:34:22"
TEST_LATER_DATETIME_STRING = "2019-12-05*10:31:20"

TEST_ANIM_NAME = Path("nair.aseprite")


def make_time(time_str=TEST_DATETIME_STRING):
    return datetime.datetime.fromisoformat(time_str)


def make_aseprite(
    path: Path,
    modified_time=make_time(),
    processed_time=None,
    anim_tag_color="green",
    window_tag_color="orange",
):
    return Aseprite(
        path=path,
        modified_time=modified_time,
        processed_time=processed_time,
        anim_tag_color=anim_tag_color,
        window_tag_color=window_tag_color,
    )


def supply_aseprites(
    tmp,
    name=TEST_ANIM_NAME,
    modified_time=make_time(),
    processed_time=None,
    relative_dest=Path("anims"),
    anim_tag_color="green",
):
    dest = Path(tmp.path) / relative_dest
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy(Path("tests/assets/sprites" / name), dest)
    return make_aseprite(
        path=dest / name,
        modified_time=modified_time,
        processed_time=processed_time,
        anim_tag_color=anim_tag_color,
    )


def make_empty_file(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        open(path, "x")
    except FileExistsError:
        pass
    assert path.exists()


def make_file(path: Path, content: str):
    make_empty_file(path)
    path.write_text(content)


def make_test_config(root_dir: Path):
    try:
        aseprite_path = (
            f"{assistant_config_mod.ASEPRITE_PATH_FIELD}: {get_aseprite_path()}"
        )
    except AssertionError:
        aseprite_path = ""

    make_file(
        root_dir / assistant_config_mod.PATH,
        content=f"""\
{assistant_config_mod.LIBRARY_UPDATE_LEVEL_FIELD}: none
{assistant_config_mod.ASSISTANT_SELF_UPDATE_FIELD}: false
{aseprite_path}
""",
    )


def assert_script_with_path(tmp, script: ScriptWithPath):
    actual_content = tmp.read(filepath=script.path.as_posix(), encoding="utf8")
    assert actual_content == script.content


def make_canvas(width, height):
    return Image.new("RGBA", (width, height))


def assert_images_equal(img1, img2):
    assert img1.height == img2.height
    assert img1.width == img2.width
    assert img1.mode == img2.mode
    img1 = img1.convert("RGB")
    img2 = img2.convert("RGB")
    assert not ImageChops.difference(img1, img2).getbbox()


def make_script(
    path: Path = PATH_A,
    original_content: str = "",
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


def get_aseprite_path():
    config = configparser.ConfigParser()
    config.read("tests/dev_config.ini")
    aseprite_path = Path(config["aseprite"]["path"])
    if aseprite_path.exists():
        return aseprite_path
    else:
        assert False, 'Aseprite is not found. Run with -v -m "not aseprite"'
