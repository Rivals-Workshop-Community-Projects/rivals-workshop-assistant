from pathlib import Path

import pytest
from testfixtures import TempDirectory
from PIL import Image, ImageDraw

import rivals_workshop_assistant.paths as paths
from rivals_workshop_assistant.asset_handling import asset_types as src
from testing_helpers import make_canvas, assert_images_equal

pytestmark = pytest.mark.slow


def test_sprite_supply():
    with TempDirectory() as tmp:
        color = 'red'
        width = 3
        height = 4
        file_name = f'{color}_rect_{width}_{height}.png'
        sprite = src.Sprite(file_name)
        root_dir = Path(tmp.path)

        sprite.supply(root_dir)

        img = Image.open(root_dir / paths.SPRITES_FOLDER / file_name)
        expected = make_canvas(width, height)
        ImageDraw.Draw(expected).rectangle((0, 0, width - 1, height - 1),
                                           fill=color,
                                           outline="black")
        assert_images_equal(img, expected)
