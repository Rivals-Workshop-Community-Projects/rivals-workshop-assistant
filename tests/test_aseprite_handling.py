import pytest
from configparser import ConfigParser
from pathlib import Path

import rivals_workshop_assistant.assistant_config_mod
import rivals_workshop_assistant.character_config_mod
from rivals_workshop_assistant.aseprite_handling import (
    Aseprite,
    AsepriteData,
    AsepriteTag,
    Anim,
    Window,
)
from tests.testing_helpers import (
    make_script,
    make_time,
)
from rivals_workshop_assistant import character_config_mod


def make_fake_aseprite(
    name="name",
    path=Path("a"),
    num_frames=1,
    tags=None,
    anim_tag_color="green",
    window_tag_color="orange",
) -> Aseprite:
    aseprite_data = AsepriteData(
        name=name,
        num_frames=num_frames,
        tags=tags,
        anim_tag_color=anim_tag_color,
        window_tag_color=window_tag_color,
    )
    aseprite = Aseprite(
        path=path,
        modified_time=make_time(),
        content=aseprite_data,
        anim_tag_color=anim_tag_color,
        window_tag_color=window_tag_color,
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

    result = rivals_workshop_assistant.character_config_mod.get_has_small_sprites(
        scripts=scripts, character_config=character_config
    )

    assert result == expected


@pytest.mark.parametrize(
    "tags, expected",
    [
        pytest.param([], [Anim(name="name", start=1, end=1)]),
        pytest.param(
            [AsepriteTag(name="name", start=1, end=2, color="red")],
            [Anim(name="name", start=1, end=2)],
        ),
        pytest.param(
            [
                AsepriteTag(name="anim_name", start=2, end=3, color="red"),
                AsepriteTag(name="window_name", start=2, end=2, color="orange"),
            ],
            [
                Anim(
                    name="anim_name",
                    start=1,
                    end=1,
                    windows=[Window(name="window_name", start=1, end=1)],
                )
            ],
        ),
    ],
)
def test_aseprite_anims(tags, expected):
    sut = make_fake_aseprite(tags=tags, anim_tag_color="red", window_tag_color="orange")

    assert sut.content.anims == expected
