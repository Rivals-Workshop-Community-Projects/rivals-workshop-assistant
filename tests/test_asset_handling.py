from pathlib import Path

import pytest

import rivals_workshop_assistant.asset_handling as src
from tests.testing_helpers import make_script, make_time, TEST_LATER_DATETIME_STRING
from rivals_workshop_assistant.asset_handling.asset_types import Sprite

from loguru import logger

logger.remove()


def test_get_required_assets__no_assets():
    result = src.get_required_assets(
        scripts=[make_script(Path("patha"), "nothing relevant")]
    )
    assert result == set()


@pytest.mark.parametrize(
    "scripts, expected",
    [
        pytest.param(
            [make_script(Path("patha"), "sprite_get('blah')")], {Sprite("blah")}
        ),
        pytest.param(
            [make_script(Path("patha"), "sprite_get('a') sprite_get('b')")],
            {Sprite("a"), Sprite("b")},
        ),
        pytest.param(
            [
                make_script(Path("patha"), "sprite_get('a' )"),
                make_script(Path("pathb"), "sprite_get( 'b')"),
            ],
            {Sprite("a"), Sprite("b")},
        ),
        pytest.param(
            [
                make_script(
                    Path("patha"),
                    "sprite_get('blah')",
                    processed_time=make_time(TEST_LATER_DATETIME_STRING),
                ),
            ],
            set(),
        ),
    ],
)
def test_get_required_assets(scripts, expected):
    result = src.get_required_assets(scripts=scripts)
    assert result == expected
