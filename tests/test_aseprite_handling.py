import pytest
from configparser import ConfigParser
from pathlib import Path

from rivals_workshop_assistant import paths
from rivals_workshop_assistant.aseprite_handling import (
    Aseprite,
    AsepriteData,
    AsepriteTag,
    Anim,
)
from tests.testing_helpers import (
    make_script,
    make_time,
)
from rivals_workshop_assistant import character_config_mod
import rivals_workshop_assistant.main as src


def make_fake_aseprite(
    path=Path("a"), num_frames=1, tags=None, anim_tag_color="green"
) -> src.Aseprite:
    # AsepriteTag('tag1', 1, 2, "red")
    aseprite_data = AsepriteData(
        num_frames=num_frames, tags=tags, anim_tag_color=anim_tag_color
    )
    aseprite = Aseprite(
        path=path,
        modified_time=make_time(),
        content=aseprite_data,
        anim_tag_color=anim_tag_color,
    )
    return aseprite


@pytest.mark.parametrize(
    "init_content, character_config_str, expected",
    [
        pytest.param("", "", False),
        pytest.param(
            "",
            f'[general]\nunrelated="1"',
            False,
        ),
        pytest.param(
            "",
            f'[general]\n{character_config_mod.SMALL_SPRITES_FIELD}="1"',
            True,
        ),
        pytest.param(
            "small_sprites=1",
            "",
            True,
        ),
        pytest.param(
            "small_sprites   =    true",
            "",
            True,
        ),
        pytest.param(
            "small_sprites=false",
            "",
            False,
        ),
        pytest.param(
            "small_sprites=0",
            "",
            False,
        ),
    ],
)
def test_get_has_small_sprites(init_content, character_config_str, expected):
    scripts = [make_script(path=Path("init.gml"), original_content=init_content)]

    character_config = ConfigParser()
    character_config.read_string(character_config_str)

    result = src.get_has_small_sprites(
        scripts=scripts, character_config=character_config
    )

    assert result == expected


@pytest.mark.parametrize(
    "tags, expected",
    [
        pytest.param([], []),
        pytest.param(
            [AsepriteTag(name="name", start=1, end=2, color="red")], [Anim(name="name")]
        ),
    ],
)
def test_aseprite_anims(tags, expected):
    sut = make_fake_aseprite(tags=tags, anim_tag_color="red")

    assert sut.content.anims == expected
