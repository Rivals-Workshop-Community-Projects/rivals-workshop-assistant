from typing import List
from configparser import ConfigParser
from pathlib import Path

import pytest

import rivals_workshop_assistant.assistant_config_mod
import rivals_workshop_assistant.character_config_mod
from rivals_workshop_assistant.aseprite_handling import (
    AsepriteTag,
    Anim,
    Window,
    TagColor,
)
from rivals_workshop_assistant.aseprite_handling.aseprites import (
    AsepriteFileContent,
    Aseprite,
)
from tests.testing_helpers import (
    make_script,
    make_time,
)
from rivals_workshop_assistant import character_config_mod


class FakeAsepriteData(AsepriteFileContent):
    def __init__(
        self,
        num_frames,
        tags,
        anim_tag_colors: List[TagColor],
        window_tag_colors: List[TagColor],
        layers,
    ):
        self._num_frames = num_frames
        self._tags = tags
        # noinspection PyTypeChecker
        super().__init__(
            anim_tag_colors,
            window_tag_colors,
            file_data=None,
            layers=layers,
        )

    @property
    def num_frames(self):
        return self._num_frames

    @property
    def tags(self):
        return self._tags


def make_fake_aseprite(
    name="name",
    path=Path("a"),
    num_frames=1,
    tags=None,
    anim_tag_color=None,
    window_tag_color=None,
    layers=None,
) -> Aseprite:
    if not anim_tag_color:
        anim_tag_color = ["green"]
    if not window_tag_color:
        window_tag_color = ["orange"]

    aseprite_data = FakeAsepriteData(
        num_frames=num_frames,
        tags=tags,
        anim_tag_colors=anim_tag_color,
        window_tag_colors=window_tag_color,
        layers=layers,
    )
    aseprite = Aseprite(
        path=path,
        modified_time=make_time(),
        content=aseprite_data,
        anim_tag_colors=anim_tag_color,
        window_tag_colors=window_tag_color,
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


def make_anim(name, start, end, windows=None, content=None):
    return Anim(
        name=name,
        start=start,
        end=end,
        windows=windows,
        content=content,
        file_is_fresh=True,
    )  # todo replace none with fake


@pytest.mark.parametrize(
    "tags, expected",
    [
        pytest.param([], [make_anim(name="a", start=0, end=0)]),
        pytest.param(
            [AsepriteTag(name="name", start=1, end=2, color="red")],
            [make_anim(name="name", start=1, end=2)],
        ),
        pytest.param(
            [
                AsepriteTag(name="anim_name", start=2, end=3, color="red"),
                AsepriteTag(name="window_name", start=2, end=2, color="orange"),
            ],
            [
                make_anim(
                    name="anim_name",
                    start=2,
                    end=3,
                    windows=[Window(name="window_name", start=1, end=1)],
                )
            ],
        ),
    ],
)
def test_aseprite_anims(tags, expected):
    sut = make_fake_aseprite(
        tags=tags, anim_tag_color=["red"], window_tag_color=["orange"]
    )

    assert sut.anims == expected
