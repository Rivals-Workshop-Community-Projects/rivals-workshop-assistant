from pathlib import Path

from PIL import Image
import pytest
from testfixtures import TempDirectory

import rivals_workshop_assistant.assistant_config_mod
from tests.testing_helpers import (
    make_empty_file,
    make_script,
    ScriptWithPath,
    create_script,
    make_script_from_script_with_path,
    supply_anim,
    TEST_ANIM_NAME,
    get_aseprite_path,
)
from rivals_workshop_assistant import paths, injection
from rivals_workshop_assistant.setup import make_basic_folder_structure
from rivals_workshop_assistant.injection import apply_injection
from rivals_workshop_assistant.paths import INJECT_FOLDER, USER_INJECT_FOLDER
from rivals_workshop_assistant.injection.dependency_handling import Define
import rivals_workshop_assistant.main as src

pytestmark = pytest.mark.slow

script_1 = ScriptWithPath(
    path=Path("scripts/script_1.gml"),
    content="""\
script 1
    content
    needs_other()
    
    
    another_func()""",
)

script_subfolder = ScriptWithPath(
    path=Path("scripts/subfolder/script_subfolder.gml"),
    content="""\
script in subfolder
func()""",
)

injection_at_root = ScriptWithPath(
    path=INJECT_FOLDER / Path("at_root.gml"),
    content="""\
#define func {
    // some docs
    //some more docs
    func content

}

#define another_func
    another func 
    content

""",
)

injection_in_subfolder = ScriptWithPath(
    path=USER_INJECT_FOLDER / Path("subfolder/in_subfolder.gml"),
    content="""\
#define needs_other {
    other()
}

#define other
    other content

""",
)

func = Define(name="func", docs="some docs\nsome more docs", content="func content")
another_func = Define(name="another_func", content="another func\ncontent")
needs_other = Define(name="needs_other", content="other()")
other = Define(name="other", content="other content")


def test_read_scripts():
    with TempDirectory() as tmp:
        create_script(tmp, script_1)
        create_script(tmp, script_subfolder)

        result = src.read_scripts(Path(tmp.path), {})

        assert result == [
            make_script_from_script_with_path(tmp, script_1),
            make_script_from_script_with_path(tmp, script_subfolder),
        ]


# TODO create test for correct times


def test_read_injection_library():
    with TempDirectory() as tmp:
        create_script(tmp, injection_at_root)
        create_script(tmp, injection_in_subfolder)

        result_library = injection.read_injection_library(Path(tmp.path))
        assert result_library == [func, another_func, needs_other, other]


def test_full_injection():
    with TempDirectory() as tmp:
        create_script(tmp, script_1)
        create_script(tmp, script_subfolder)
        create_script(tmp, injection_at_root)
        create_script(tmp, injection_in_subfolder)

        scripts = src.read_scripts(Path(tmp.path), {})
        library = injection.read_injection_library(Path(tmp.path))
        result_scripts = apply_injection(scripts=scripts, injection_library=library)

        expected_script_1 = f"""\
{script_1.content}

{injection.application.INJECTION_START_HEADER}
{another_func.gml}

{needs_other.gml}

{other.gml}
{injection.application.INJECTION_END_HEADER}"""

        expected_subfolder = f"""\
{script_subfolder.content}

{injection.application.INJECTION_START_HEADER}
{func.gml}
{injection.application.INJECTION_END_HEADER}"""

        assert result_scripts == [
            make_script(
                script_1.absolute_path(tmp),
                original_content=script_1.content,
                working_content=expected_script_1,
            ),
            make_script(
                script_subfolder.absolute_path(tmp),
                original_content=script_subfolder.content,
                working_content=expected_subfolder,
            ),
        ]

        src.save_scripts(root_dir=Path(tmp.path), scripts=result_scripts)

        actual_script_1 = tmp.read(script_1.path.as_posix(), encoding="utf8")
        assert actual_script_1 == expected_script_1

        actual_script_subfolder = tmp.read(
            script_subfolder.path.as_posix(), encoding="utf8"
        )
        assert actual_script_subfolder == expected_subfolder


def test__make_basic_folder_structure__make_missing_config():
    with TempDirectory() as tmp:
        make_basic_folder_structure(Path(tmp.path))

        actual = (
            Path(tmp.path) / rivals_workshop_assistant.assistant_config_mod.PATH
        ).read_text()
        assert actual == rivals_workshop_assistant.assistant_config_mod.DEFAULT_CONFIG


def test__make_basic_folder_structure__config_present():
    with TempDirectory() as tmp:
        config_path = (
            Path(tmp.path) / rivals_workshop_assistant.assistant_config_mod.PATH
        )
        create_script(tmp, ScriptWithPath(path=config_path, content="a"))

        make_basic_folder_structure(Path(tmp.path))

        actual = config_path.read_text()
        assert actual == "a"


def test__read_anims():
    with TempDirectory() as tmp:
        supply_anim(tmp, TEST_ANIM_NAME)

        result = src.read_aseprites(root_dir=Path(tmp.path), dotfile={})
        assert len(result) == 1
        assert result[0].path == Path(tmp.path) / "anims" / TEST_ANIM_NAME
        assert result[0].is_fresh


def assert_anim(
    root_dir, filename=f"{TEST_ANIM_NAME.stem}_strip3.png", has_small_sprites=False
):
    """Right now this assumes that the sprite is the absa dashstart anim stored in
    TEST_ANIM_NAME"""
    with Image.open(root_dir / paths.SPRITES_FOLDER / filename) as img:
        assert img.height == 66 * (int(has_small_sprites) + 1)
        assert img.width == 76 * 3 * (int(has_small_sprites) + 1)


@pytest.mark.parametrize("has_small_sprites", [pytest.param(False), pytest.param(True)])
def test__save_anims(has_small_sprites):
    aseprite_path = get_aseprite_path()

    with TempDirectory() as tmp:
        root_dir = Path(tmp.path)
        anims = [supply_anim(tmp)]

        src.save_aseprites(
            root_dir=root_dir,
            aseprite_path=Path(aseprite_path),
            aseprites=anims,
            has_small_sprites=has_small_sprites,
        )

        assert_anim(root_dir, has_small_sprites=has_small_sprites)


def test__save_anims__uses_subfolder_name():
    subfolder_name = "subfolder"
    aseprite_path = get_aseprite_path()

    with TempDirectory() as tmp:
        root_dir = Path(tmp.path)
        anims = [supply_anim(tmp, relative_dest=Path("anims") / subfolder_name)]

        src.save_aseprites(
            root_dir=root_dir,
            aseprite_path=Path(aseprite_path),
            aseprites=anims,
            has_small_sprites=False,
        )

        assert_anim(
            root_dir,
            filename=f"{subfolder_name}_{TEST_ANIM_NAME.stem}_strip3.png",
            has_small_sprites=False,
        )


def test__save_anims__removes_old_spritesheet():
    aseprite_path = get_aseprite_path()

    with TempDirectory() as tmp:
        root_dir = Path(tmp.path)
        anims = [supply_anim(tmp)]
        old_filename = (
            root_dir / paths.SPRITES_FOLDER / f"{TEST_ANIM_NAME.stem}_strip2.png"
        )
        make_empty_file(old_filename)
        other_filename = root_dir / paths.SPRITES_FOLDER / f"unrelated_strip2.png"
        make_empty_file(other_filename)

        src.save_aseprites(
            root_dir=root_dir,
            aseprite_path=Path(aseprite_path),
            aseprites=anims,
            has_small_sprites=False,
        )

        assert not old_filename.exists()
        assert other_filename.exists()


def test__save_anims__removes_old_spritesheet__with_subfolder():
    aseprite_path = get_aseprite_path()
    subfolder_name = "subfolder"

    with TempDirectory() as tmp:
        root_dir = Path(tmp.path)
        anims = [supply_anim(tmp, relative_dest=Path("anims") / subfolder_name)]
        old_filename = (
            root_dir
            / paths.SPRITES_FOLDER
            / f"{subfolder_name}_{TEST_ANIM_NAME.stem}_strip2.png"
        )
        make_empty_file(old_filename)
        other_filename = (
            root_dir / paths.SPRITES_FOLDER / f"{subfolder_name}_unrelated_strip2.png"
        )
        make_empty_file(other_filename)

        src.save_aseprites(
            root_dir=root_dir,
            aseprite_path=Path(aseprite_path),
            aseprites=anims,
            has_small_sprites=False,
        )

        assert not old_filename.exists()
        assert other_filename.exists()
