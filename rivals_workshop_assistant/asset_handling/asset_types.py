import re
from pathlib import Path
import abc

from rivals_workshop_assistant import paths
from .sprite_generation import make_sprite_for_file_name


class Asset(abc.ABC):
    def __init__(self, asset_string: str):
        self.asset_string = asset_string

    @classmethod
    def get_from_text(cls, text) -> set['Asset']:
        raise NotImplementedError

    def supply(self, path: Path) -> None:
        raise NotImplementedError

    def __eq__(self, other):
        return self.asset_string == other.asset_string

    def __hash__(self):
        return hash(self.__class__.__name__ + self.asset_string)


class Sprite(Asset):
    _pattern = r"(?<=sprite_get\([\"'])(.+?)(?=['\"]\))"

    @classmethod
    def get_from_text(cls, text) -> set['Sprite']:
        asset_strings = set(re.findall(pattern=cls._pattern, string=text))
        return set(Sprite(string) for string in asset_strings)

    def supply(self, path: Path):
        sprite_path = path / paths.SPRITES_FOLDER
        make_sprite_for_file_name(
            sprite_path=sprite_path, file_name=self.asset_string)


ASSET_TYPES = [Sprite]
