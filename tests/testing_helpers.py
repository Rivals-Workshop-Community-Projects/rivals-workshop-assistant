import configparser
import datetime
import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from testfixtures import TempDirectory

import rivals_workshop_assistant.updating
from rivals_workshop_assistant import assistant_config_mod
from rivals_workshop_assistant.script_mod import Script
from rivals_workshop_assistant.aseprite_handling.aseprites import Aseprite

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
TEST_EARLIER_DATETIME_STRING = "2019-12-03*09:34:22"
TEST_DATETIME_STRING = "2019-12-04*09:34:22"
TEST_LATER_DATETIME_STRING = "2019-12-05*10:31:20"

TEST_ANIM_NAME = Path("nair.aseprite")


def make_time(time_str=TEST_DATETIME_STRING):
    return datetime.datetime.fromisoformat(time_str)


def make_aseprite(
    path: Path,
    modified_time=make_time(),
    processed_time=None,
    anim_tag_colors=None,
    window_tag_colors=None,
):
    if not anim_tag_colors:
        anim_tag_colors = ["green"]
    if not window_tag_colors:
        window_tag_colors = ["orange"]
    return Aseprite(
        path=path,
        modified_time=modified_time,
        processed_time=processed_time,
        anim_tag_colors=anim_tag_colors,
        window_tag_colors=window_tag_colors,
    )


def supply_aseprites(
    tmp,
    name=TEST_ANIM_NAME,
    modified_time=make_time(),
    processed_time=None,
    relative_dest=Path("anims"),
    anim_tag_colors=None,
    window_tag_colors=None,
):
    if not anim_tag_colors:
        anim_tag_colors = ["green"]
    if not window_tag_colors:
        window_tag_colors = ["orange"]
    dest = Path(tmp.path) / relative_dest
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy(Path("tests/assets/sprites") / name, dest)
    return make_aseprite(
        path=dest / name,
        modified_time=modified_time,
        processed_time=processed_time,
        anim_tag_colors=anim_tag_colors,
        window_tag_colors=window_tag_colors,
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
    if img1.mode == img2.mode == "RGBA":
        img1_alphas = [pixel[3] for pixel in img1.getdata()]
        img2_alphas = [pixel[3] for pixel in img2.getdata()]
        assert img1_alphas == img2_alphas
    assert all(
        are_pixels_equal(px1, px2) for px1, px2 in zip(img1.getdata(), img2.getdata())
    )


def get_px_alpha(px):
    if len(px) == 4:
        return px[3]
    else:
        return 255


def are_pixels_equal(px1, px2):
    if isinstance(px1, int):
        if isinstance(px2, int):
            return px1 == px2
            # Technically I think this is incomplete.
            # It tests that the index for the color palette is the same, but not necessarily that the color is correct.
        else:
            return False

    alphas = [get_px_alpha(px) for px in (px1, px2)]
    if alphas[0] != alphas[1]:
        return False

    if alphas[0] == 0:
        return True  # They're both transparent, doesn't matter what their RGB is.

    for color_index in range(3):
        if px1[color_index] != px2[color_index]:
            return False
    return True


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
