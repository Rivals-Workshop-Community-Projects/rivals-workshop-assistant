from pathlib import Path

import pytest

import rivals_workshop_assistant.asset_handling as src
from rivals_workshop_assistant.asset_handling.asset_types import Sprite


def test_get_required_assets__no_assets():
    result = src.get_required_assets(
        scripts={Path('patha'): 'nothing relevant'}
    )
    assert result == set()


@pytest.mark.parametrize(
    "scripts, expected",
    [
        pytest.param(
            {Path('patha'): "sprite_get('blah')"},
            {Sprite('blah')}
        ),
        pytest.param(
            {Path('patha'): "sprite_get('a')"
                            "sprite_get('b')"},
            {Sprite('a'), Sprite('b')}
        ),
        pytest.param(
            {Path('patha'): "sprite_get('a')",
             Path('pathb'): "sprite_get('b')"},
            {Sprite('a'), Sprite('b')}
        ),
    ]
)
def test_get_required_assets(scripts, expected):
    result = src.get_required_assets(
        scripts={Path('patha'): "sprite_get('blah')"}
    )
    assert result == {Sprite('blah')}
