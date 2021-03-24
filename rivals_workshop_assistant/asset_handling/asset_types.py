import re
from pathlib import Path
import abc

from rivals_workshop_assistant import paths
from .sprite_generation import generate_sprite_for_file_name


class Asset(abc.ABC):
    def __init__(self, asset_string: str):
        self.asset_string = asset_string

    @classmethod
    def get_from_text(cls, text) -> set['Asset']:
        raise NotImplementedError

    def supply(self, root_dir: Path) -> None:
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

    def supply(self, root_dir: Path):
        file_name = self.asset_string
        path = root_dir / paths.SPRITES_FOLDER / file_name
        if not path.exists():
            sprite = generate_sprite_for_file_name(file_name)
            if sprite:
                path.parent.mkdir(parents=True, exist_ok=True)
                sprite.save(path)


ASSET_TYPES = [Sprite]
