from pathlib import Path

import pytest
from PIL import Image
from testfixtures import TempDirectory

from rivals_workshop_assistant import paths
from rivals_workshop_assistant.aseprite_handling import (
    AsepritePathParams,
    AsepriteConfigParams,
)
from rivals_workshop_assistant.aseprite_handling.aseprites import read_aseprite
from rivals_workshop_assistant.assistant_config_mod import ANIM_TAG_COLOR_FIELD
from tests.testing_helpers import (
    get_aseprite_path,
    assert_images_equal,
)
from loguru import logger

logger.remove()
pytestmark = pytest.mark.slow

TEST_SPRITES_PATH = Path("tests/assets/sprites")


def load_test_image(name: str):
    with Image.open(TEST_SPRITES_PATH / name) as img:
        return img


async def assert_aseprite_saves_right_anims(
    aseprite_file_name: str,
    save_file_names: list[str],
    expected_file_names: list[str],
    expected_missing_file_names: list[str] = None,
    dotfile: dict = None,
    assistant_config: dict = None,
    has_small_sprites: bool = False,
    hurtboxes_enabled: bool = False,
):
    if expected_missing_file_names is None:
        expected_missing_file_names = []
    if dotfile is None:
        dotfile = {}
    if assistant_config is None:
        assistant_config = {}

    aseprite_path = get_aseprite_path()

    path = TEST_SPRITES_PATH / f"{aseprite_file_name}.aseprite"
    aseprite = read_aseprite(
        path=path, dotfile=dotfile, assistant_config=assistant_config
    )
    with TempDirectory() as root_dir, TempDirectory() as exe_dir:
        root_dir = Path(root_dir.path)
        await aseprite.save(
            path_params=AsepritePathParams(
                exe_dir=Path(exe_dir.path),
                root_dir=root_dir,
                aseprite_program_path=aseprite_path,
            ),
            config_params=AsepriteConfigParams(
                has_small_sprites=has_small_sprites,
                hurtboxes_enabled=hurtboxes_enabled,
            ),
        )

        for save_file_name, expected_file_name in zip(
            save_file_names, expected_file_names
        ):
            actual_path = root_dir / paths.SPRITES_FOLDER / f"{save_file_name}.png"
            expected_path = TEST_SPRITES_PATH / f"{expected_file_name}.png"
            with Image.open(actual_path) as actual, Image.open(
                expected_path
            ) as expected:
                assert_images_equal(actual, expected)

        for expected_missing_file_name in expected_missing_file_names:
            expected_missing_path = (
                root_dir / paths.SPRITES_FOLDER / f"{expected_missing_file_name}.png"
            )
            with pytest.raises(FileNotFoundError):
                Image.open(expected_missing_path)


@pytest.mark.parametrize(
    "aseprite_file_name, save_file_names, expected_file_names",
    [
        # pytest.param("1frame", ["1frame_strip1"], ["1frame"]),
        # pytest.param("2frame", ["2frame_strip2"], ["2frame"]),
        # pytest.param("2frame_with_groups", ["2frame_with_groups_strip2"], ["2frame"]),
        # pytest.param(
        #     "1frame_2frame", ["1frame_strip1", "2frame_strip2"], ["1frame", "2frame"]
        # ),
        # pytest.param(
        #     "1frame_2frame_red_tag",
        #     ["1frame_2frame_red_tag_strip3"],
        #     ["1frame_2frame"],
        # ),
        # pytest.param(
        #     "1frame_1bair",
        #     ["1frame_strip1", "bair_strip1"],
        #     ["1frame", "bair_big"],
        # ),
        # pytest.param(
        #     "1frame_hurtmask",
        #     ["1frame_hurtmask_strip1"],
        #     ["1frame"],
        # ),
        # pytest.param(
        #     "1frame_hurtbox_layer",
        #     ["1frame_hurtbox_layer_strip1"],
        #     ["1frame"],
        # ),
        # pytest.param(
        #     # Layers called "Flattened" were once problematic because the layer name was
        #     # used in the lua script
        #     "1has_flattened",
        #     ["1has_flattened_strip1"],
        #     ["1has_flattened"],
        # ),
        # pytest.param(
        #     "1frame_with_hidden_above", ["1frame_with_hidden_above_strip1"], ["1frame"]
        # ),
        pytest.param(
            "1frame_with_hidden_below", ["1frame_with_hidden_below_strip1"], ["1frame"]
        ),
    ],
)
@pytest.mark.aseprite
@pytest.mark.asyncio
async def test_aseprite_save(aseprite_file_name, save_file_names, expected_file_names):
    await assert_aseprite_saves_right_anims(
        aseprite_file_name=aseprite_file_name,
        save_file_names=save_file_names,
        expected_file_names=expected_file_names,
    )


@pytest.mark.parametrize(
    "aseprite_file_name, save_file_names, expected_file_names",
    [
        pytest.param("1frame_2frame", ["1frame_2frame_strip3"], ["1frame_2frame"]),
        pytest.param(
            "1frame_2frame_red_tag",
            ["1frame_strip1", "2frame_strip2"],
            ["1frame", "2frame"],
        ),
    ],
)
@pytest.mark.aseprite
@pytest.mark.asyncio
async def test_aseprite_save__red_anim_tags(
    aseprite_file_name, save_file_names, expected_file_names
):
    await assert_aseprite_saves_right_anims(
        aseprite_file_name=aseprite_file_name,
        save_file_names=save_file_names,
        expected_file_names=expected_file_names,
        assistant_config={ANIM_TAG_COLOR_FIELD: "red"},
    )


@pytest.mark.parametrize(
    "aseprite_file_name, save_file_names, expected_file_names",
    [
        pytest.param("1frame", ["1frame_strip1"], ["1frame"]),  # Don't make small
        pytest.param(
            "1frame_1bair",
            ["1frame_strip1", "bair_strip1"],
            ["1frame", "bair"],
        ),
    ],
)
@pytest.mark.aseprite
@pytest.mark.asyncio
async def test_aseprite_save__small_sprites(
    aseprite_file_name, save_file_names, expected_file_names
):
    await assert_aseprite_saves_right_anims(
        aseprite_file_name=aseprite_file_name,
        save_file_names=save_file_names,
        expected_file_names=expected_file_names,
        has_small_sprites=True,
    )


@pytest.mark.parametrize(
    "aseprite_file_name, save_file_names, expected_file_names, expected_missing_file_names",
    [
        pytest.param("fair", [], [], ["fair_hurt_strip1"]),
    ],
)
@pytest.mark.aseprite
@pytest.mark.asyncio
async def test_aseprite_save__no_hurtbox(
    aseprite_file_name,
    save_file_names,
    expected_file_names,
    expected_missing_file_names,
):
    await assert_aseprite_saves_right_anims(
        aseprite_file_name=aseprite_file_name,
        save_file_names=save_file_names,
        expected_file_names=expected_file_names,
        expected_missing_file_names=expected_file_names,
        hurtboxes_enabled=False,
    )


@pytest.mark.parametrize(
    "aseprite_file_name, "
    "save_file_names, "
    "expected_file_names, "
    "expected_missing_file_names",
    [
        pytest.param("1frame", [], [], ["1frame_hurt_strip1"]),
        pytest.param(
            "1frame_1bair", ["bair_hurt_strip1"], ["bair_hurt"], ["1frame_hurt_strip1"]
        ),
        pytest.param(
            "wrong_color_type", ["fair_hurt_strip1"], ["wrong_color_type"], []
        ),
        pytest.param("with_hidden_layer", ["bair_hurt_strip1"], ["bair_hurt"], []),
    ],
)
@pytest.mark.aseprite
@pytest.mark.asyncio
async def test_aseprite_save_hurtbox(
    aseprite_file_name,
    save_file_names,
    expected_file_names,
    expected_missing_file_names,
):
    await assert_aseprite_saves_right_anims(
        aseprite_file_name=aseprite_file_name,
        save_file_names=save_file_names,
        expected_file_names=expected_file_names,
        expected_missing_file_names=expected_missing_file_names,
        hurtboxes_enabled=True,
    )


@pytest.mark.parametrize(
    "aseprite_file_name, "
    "save_file_names, "
    "expected_file_names, "
    "expected_missing_file_names",
    [  # Note that each input needs to have an attack name, or it won't generate a hurtbox
        pytest.param("fair", ["fair_hurt_strip1"], ["fair_hurt"], []),
        pytest.param("dair", ["dair_hurt_strip1"], ["fair_hurt"], []),
        pytest.param(
            "1blah_1fair", ["fair_hurt_strip1"], ["fair_hurt"], ["blah_hurt_strip1"]
        ),
        pytest.param(
            "1blah_2uair_1blah",
            ["uair_hurt_strip2"],
            ["uair_hurt"],
            ["blah_hurt_strip1", "blah2_hurt_strip1"],
        ),
    ],
)
@pytest.mark.aseprite
@pytest.mark.asyncio
async def test_aseprite_save_hurtbox__with_hurtmask(
    aseprite_file_name,
    save_file_names,
    expected_file_names,
    expected_missing_file_names,
):
    await assert_aseprite_saves_right_anims(
        aseprite_file_name=aseprite_file_name,
        save_file_names=save_file_names,
        expected_file_names=expected_file_names,
        expected_missing_file_names=expected_missing_file_names,
        hurtboxes_enabled=True,
    )


@pytest.mark.parametrize(
    "aseprite_file_name, "
    "save_file_names, "
    "expected_file_names, "
    "expected_missing_file_names",
    [
        pytest.param(
            "1blah_1ftilt", ["ftilt_hurt_strip1"], ["ftilt_hurt"], ["blah_hurt_strip1"]
        ),
        pytest.param(
            "1blah_1ftilt_with_mask",
            ["ftilt_hurt_strip1"],
            ["ftilt_hurt_with_mask"],
            ["blah_hurt_strip1"],
        ),
    ],
)
@pytest.mark.aseprite
@pytest.mark.asyncio
async def test_aseprite_save_hurtbox__with_hurtbox_layer(
    aseprite_file_name,
    save_file_names,
    expected_file_names,
    expected_missing_file_names,
):
    await assert_aseprite_saves_right_anims(
        aseprite_file_name=aseprite_file_name,
        save_file_names=save_file_names,
        expected_file_names=expected_file_names,
        expected_missing_file_names=expected_missing_file_names,
        hurtboxes_enabled=True,
    )


@pytest.mark.parametrize(
    "aseprite_file_name, "
    "save_file_names, "
    "expected_file_names, "
    "expected_missing_file_names",
    [
        pytest.param(
            "hurt_layers_fair", ["fair_hurt_strip1"], ["hurt_layers_fair"], []
        ),
        pytest.param(
            "nohurt_meta_fair", ["fair_hurt_strip1"], ["nohurt_meta_fair"], []
        ),
    ],
)
@pytest.mark.aseprite
@pytest.mark.asyncio
async def test_aseprite_save_hurtbox__with_nohurt_layers(
    aseprite_file_name,
    save_file_names,
    expected_file_names,
    expected_missing_file_names,
):
    await assert_aseprite_saves_right_anims(
        aseprite_file_name=aseprite_file_name,
        save_file_names=save_file_names,
        expected_file_names=expected_file_names,
        expected_missing_file_names=expected_missing_file_names,
        hurtboxes_enabled=True,
    )


@pytest.mark.parametrize(
    "aseprite_file_name, "
    "save_file_names, "
    "expected_file_names, "
    "expected_missing_file_names",
    [
        pytest.param(
            "split_blah1",
            ["split_blah1_strip1", "split_blah1_blah_strip1"],
            ["split_blah1_normal", "split_blah1_blah"],
            [],
        ),
        pytest.param(
            "split_onlyblah_blah1",
            ["split_onlyblah_blah1_blah_strip1"],
            ["split_blah1_blah"],
            [],
        ),
        pytest.param(
            "split_blah1_2layers",
            ["split_blah1_2layers_strip1", "split_blah1_2layers_blah_strip1"],
            ["split_blah1_normal", "split_blah1_blahleftright"],
            [],
        ),
        pytest.param(
            "split_foobar1",
            [
                "split_foobar1_strip1",
                "split_foobar1_foo_strip1",
                "split_foobar1_bar_strip1",
            ],
            ["split_blah1_normal", "split_blah1_blah", "split_foobar_bar"],
            [],
        ),
        pytest.param(
            "split_foobar1_groups",
            [
                "split_foobar1_groups_strip1",
                "split_foobar1_groups_foo_strip1",
                "split_foobar1_groups_bar_strip1",
            ],
            ["split_blah1_normal", "split_blah1_blah", "split_foobar_bar"],
            [],
        ),
    ],
)
@pytest.mark.aseprite
@pytest.mark.asyncio
async def test_aseprite_export__with_splits(
    aseprite_file_name,
    save_file_names,
    expected_file_names,
    expected_missing_file_names,
):

    await assert_aseprite_saves_right_anims(
        aseprite_file_name=aseprite_file_name,
        save_file_names=save_file_names,
        expected_file_names=expected_file_names,
        expected_missing_file_names=expected_missing_file_names,
        hurtboxes_enabled=True,
    )


@pytest.mark.parametrize(
    "aseprite_file_name, "
    "save_file_names, "
    "expected_file_names, "
    "expected_missing_file_names",
    [
        pytest.param(
            "opt_hat",
            ["opt_hat_strip1", "opt_hat_hat_strip1"],
            ["opt_hat", "opt_hat_hat"],
            [],
        ),
    ],
)
@pytest.mark.aseprite
@pytest.mark.asyncio
async def test_aseprite_export__with_opts(
    aseprite_file_name,
    save_file_names,
    expected_file_names,
    expected_missing_file_names,
):

    await assert_aseprite_saves_right_anims(
        aseprite_file_name=aseprite_file_name,
        save_file_names=save_file_names,
        expected_file_names=expected_file_names,
        expected_missing_file_names=expected_missing_file_names,
        hurtboxes_enabled=True,
    )
